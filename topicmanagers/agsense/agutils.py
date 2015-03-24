from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tlsettings import tlConstants as Constants
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tlbrokers import tlBrokers as Brokers
from TelemetryLayer.tlmqttclient import *
from TelemetryLayer.topicmanagers.agsense.agdevice import agDeviceList, agDevice, agParams, agParam

import os.path,sys,traceback,json




class tlTableParam(QObject):
    """
    Todo: refactor this - place Table Parameter handling into
    package of dialog widget utils
    
    """
    kLabel = 0
    kControl = 1

    """
    Populates a table widget with a set of widgets (one one per row) defined by deviceType
    Todo: add isDirty method - currently dirty regardless
    """

    def __init__(self, tbl, row, param, default=None):
        super(tlTableParam, self).__init__()
        tbl.insertRow(row)

        self.row = row
        self.tbl = tbl
        self.value = default
        self.control = QWidget()

        try:
            self.name    = param['name']
            self.title   = param['title']
            self.tooltip = param['desc']
            self.type    = param['type']
            self.default = default
            
            self.readonly= param['readonly']

        except TypeError as e:
            Log.warn('Type error creating paramater widget ' + str(e))

        item = QtGui.QLabel(self.title, self.tbl)
        item.setStyleSheet("padding: 4px")
        item.setWordWrap(True)
        item.setToolTip(self.tooltip)

        self.tbl.setCellWidget(row, self.kLabel, item)

        item = QtGui.QTableWidgetItem(0)
        item.setFlags(QtCore.Qt.NoItemFlags)
        tbl.setItem(row, self.kLabel, item)

        pass

    def _setControl(self, height=None):
        self.tbl.setCellWidget(self.row, self.kControl, self.control)
        self.control.setEnabled(not self.readonly)
        item = QtGui.QTableWidgetItem(0)
        item.setFlags(QtCore.Qt.NoItemFlags)
        self.tbl.setItem(self.row, self.kLabel, item)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        if height is not None:
            self.tbl.setRowHeight(self.row, height)


    def getName(self):
        try:
            return self.name
        except:
            return None

    def getTitle(self):
        return self.title

    def getValue(self):
        return self.value

    def getType(self):
        return self.type


# Create a spin box

class tlTableParamSpinBox(tlTableParam):
    def __init__(self, tbl, row, param, default=None):
        super(tlTableParamSpinBox, self).__init__(tbl, row, param, default)

        try:
            self.min = param['min']
            self.max = param['max']
            self.int = param['interval']
            self.units = param['units']
            try:
                self.step = param['step']
            except:
                self.step = "1"

            self.control = QtGui.QSpinBox(self.tbl)
            self.control.setMinimum(int(self.min) - 1)  # Qt Bug Min is actual > not >=
            self.control.setMaximum(int(self.max))
            self.control.setSingleStep(int(self.step))  # ???
            self.control.setToolTip(self.tooltip)
            self.control.setSuffix('\x0A' + self.units)
            self.control.setStyleSheet("padding: 4px")
            self.control.valueChanged.connect(self.setValue)
            self._setControl(40)
            self.control.setValue(int(self.default))
           # self.control.valueChanged.connect(self.setDirty)

        except Exception as e:
            Log.debug('Error loading parameter widget ' + str(e))
            return

        pass

    def setValue(self, value):
        self.value = value


class tlTableParamCheckBox(tlTableParam):
    def __init__(self, tbl, row, param, default=None):
        super(tlTableParamCheckBox, self).__init__(tbl, row, param, default)

        try:
            self.control = QtGui.QCheckBox(self.tbl)
            self.control.setToolTip(self.tooltip)
            self.control.setStyleSheet("padding: 4px")
            self.control.stateChanged.connect(self.setValue)
            self.control.setTristate(False);
            self._setControl(40)
            self.control.setChecked(self.default == 'On')


        except Exception as e:
            Log.debug('Error loading parameter widget ' + str(e))
            return

        pass

    def setValue(self, value):
        self.value = value
        
    def getValue(self):
       if self.control.isChecked():
            return 'On'
       else:
            return 'Off'


# Create a Slider

class tlTableParamSlider(tlTableParam):
    def __init__(self, tbl, row, param, default=None):

        super(tlTableParamSlider, self).__init__(tbl, row, param, default)
        try:
            self.min = param['min']
            self.max = param['max']
            self.int = param['interval']
            self.units = param['units']
            try:
                self.step = param['step']
            except:
                self.step = "1"

            # Only handles Integers currently!

            self.control = QtGui.QSlider(QtCore.Qt.Horizontal, self.tbl)
            self.control.setStyleSheet("padding: 4px")
            self.control.setFocusPolicy(QtCore.Qt.ClickFocus)
            # self.control.setTickPosition(QtGui.QSlider.TicksBelow)
            #self.control.setTickInterval(int(float(self.max)/50))
            self.control.setSingleStep(int(self.step))
            self.control.setMinimum(int(self.min))
            self.control.setMaximum(int(self.max))
            self.control.setToolTip(self.tooltip)
            self.control.valueChanged.connect(self.setValue)
            self._setControl(50)
            self.control.setValue(int(self.default))

        except Exception as e:
            Log.warn('Error creating widget parameter ' + str(e))
            return

    def setValue(self, value):
        self.value = value
        item = self.tbl.cellWidget(self.row, self.kLabel)
        item.setText(self.title + ' ' + str(value) + ' ' + self.units)
        pass


# Create a Dropdown

class tlTableParamCombo(tlTableParam):
    def __init__(self, tbl, row, param, default=None):

        super(tlTableParamCombo, self).__init__(tbl, row, param, default)

        # Only handles Integers currently!

        self.control = QtGui.QComboBox(tbl)
        self.control.setToolTip(self.tooltip)
        idx = 0
        defidx = 0
        for option in param['options']:
            self.control.insertItem(idx, option.text, option)
            if hasattr(option,'value') and option['value'] == self.default:
                defidx = idx
            idx += 1

        self.control.currentIndexChanged.connect(self.setValue)
        self.control.setToolTip(self.tooltip)
        self._setControl()
        # self.tbl.setRowHeight(row,100)
        self.control.setCurrentIndex(defidx)

    def setValue(self, idx):
        self.value = self.control.itemData(idx).get('value')
        pass


"""
Populate a Combo Box with widgets to handle server
based parameters defined in device types, and return
values to be stored in the device map.

"""


class agParameterTable(QObject):
    _params = []

    def __init__(self,  tableWidget, params):
        super(agParameterTable, self).__init__()
        _params = params
        self._params =[]

        tblParam = tableWidget
        tblParam.horizontalHeader().setVisible(False)
        tblParam.verticalHeader().setVisible(False)

        tblParam.clearContents()
        tblParam.setRowCount(0)
        tblParam.setShowGrid(True)
        tblParam.setColumnCount(2)
        
        if _params is None or len(_params) == 0:
            return

        # Create a table of controls preset with existing values if required
        try:

            for param in _params:
                if 'value' in param: 
                    default = param['value']
                else:
                    default = param['default']
    
                if param['widget'] == 'slider':
                    self._params.append(tlTableParamSlider(tblParam, tblParam.rowCount(), param, default))
                if param['widget'] == 'select':
                    self._params.append(tlTableParamCombo(tblParam, tblParam.rowCount(), param, default))
                if param['widget'] == 'spinbox':
                    self._params.append(tlTableParamSpinBox(tblParam, tblParam.rowCount(), param, default))
                if param['widget'] == 'checkbox':
                    self._params.append(tlTableParamCheckBox(tblParam, tblParam.rowCount(), param, default))
        except KeyError as e:
            Log.warn("Error parsing configuration parameters " + str(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.debug(repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback)))

    def params(self):
        params = {}
        for param in self._params:
            params[param.getName()] = param.getValue()

        return params
    
    def __iter__(self):
        return self.params().iteritems()

class agConfigView(QObject):
    def __init__(self, tabs, tLayer, feature): # change to broker?
        super(agConfigView, self).__init__()
        self._tabs = tabs
        self._feature = feature
        self._broker = tLayer.getBroker()
        self._topicManager = tLayer.topicManager()
        self._pTable = None
        self._rebuild()
        self._tabs.btnApply.clicked.connect(self._apply)
        self._tabs.btnReload.clicked.connect(self._reload)

    def _rebuild(self,mqtt =None, status = True, msg = None):
        if not status:
            Log.progress("There was an error reading the device configurations for this broker: " +str(msg));
            return
        try:
            topic = self._broker.topic(self._feature['topic'])
            self._params = topic['params']
            self._pTable = agParameterTable(self._tabs.tblParams, self._params)
#            self._tabs.btnApply.setEnabled(False)
        except Exception as e:
            Log.debug("Error loading Configuration tab " + str(e))

    def _reload(self):
        self._topicManager._requestDevices(self._rebuild)

    def _updateBroker(self,mqtt, status = True, msg = None):
            Log.debug("_updateBroker! " + str(status))
            if not status:  
                Log.warn(msg)
                return
            self._topicManager.setDevices(agDeviceList(msg.payload))
            self._broker.setTopics(self._topicManager.getTopics())
            self._broker.setDirty(True)
            Brokers.instance().update(self._broker)
            Brokers.instance().sync(True)
            Log.debug("Broker updated")

    def _applied(self, client, status = True, msg = None):
        if status == False:
            Log.progress("Unable to update device settings - restoring")
            self._rebuild()
        else:
            Log.progress("Configuration updated")
            Log.debug("Updating Devices")
            self._topicManager._requestDevices(self._updateBroker)
        pass
    
    def _apply(self):
        _client  = None
        try:
            params = {"topic":self._feature['topic']}
            for key,val in self._pTable:
                params[key] = val
            payload = json.dumps(params)
            request = "agsense/request/set"
            Log.progress("Updating configuration")
        
            _client = tlMqttSingleShot(self,
                                    self._broker,
                                    request,
                                    ["agsense/response/set"],
                                    payload,
                                    0, #qos
                                    self._applied)
            
            _client.run()
        except Exception as e:
            Log.debug("Error setting parameter " + str(e))
            if _client:
                _client.kill()


    def show(self):
        pass

    def update(self, data):
        pass

    def _error(self, mqtt, msg=""):
        Log.progress(msg)
