# -*- coding: utf-8 -*-
"""
/***************************************************************************
 dsFeatureDialog
 
 Charting and Data panels of the custom feature dialog

 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from TelemetryLayer.tltopicmanager import tlTopicManager, tlFeatureDialog
from TelemetryLayer.lib.tlsettings import tlSettings as Settings, tlConstants as Constants
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tlmqttclient import *

from ui_agdatatabwidget import Ui_Form
import os, zlib, datetime, json, numpy


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class tlTableParam(QObject):
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


        except Exception as e:
            Log.debug('Error loading parameter widget ' + str(e))
            return

        pass

    def setValue(self, value):
        self.value = value


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
            self.control.setFocusPolicy(QtCore.Qt.ClickFocus)
            # self.control.setTickPosition(QtGui.QSlider.TicksBelow)
            #self.control.setTickInterval(int(float(self.max)/50))
            self.control.setSingleStep(int(self.step))
            self.control.setMinimum(int(self.min))
            self.control.setMaximum(int(self.max))
            self.control.setToolTip(self.tooltip)
            self.control.setStyleSheet("padding: 4px")
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
            if option['value'] == self.default:
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
                default = param['value']
    
                if param['widget'] == 'slider':
                    self._params.append(tlTableParamSlider(tblParam, tblParam.rowCount(), param, default))
                if param['widget'] == 'select':
                    self._params.append(tlTableParamCombo(tblParam, tblParam.rowCount(), param, default))
                if param['widget'] == 'spinbox':
                    self._params.append(tlTableParamSpinBox(tblParam, tblParam.rowCount(), param, default))
        except KeyError as e:
            Log.warn(e)

    def params(self):
        params = {}
        for param in self._params:
            # Log.debug("Setting " + param.getName() + " to " + str(param.getValue()))
            params[param.getName()] = param.getValue()

        return params



class agDataTab(QDialog, Ui_Form):
    def __init__(self):
        Log.debug("Init form")
        try:
            super(agDataTab, self).__init__()
            self.setupUi(self)
        except Exception as e:
            Log.debug(e)


class agDataView(QObject):
    def __init__(self, tLayer, feature):
        super(agDataView, self).__init__()

    def _request(self, interval, duration):
        pass

    def _update(self, client, status, msg):
        pass

class agDataLoggerView(agDataView):
    def __init__(self, tabs, tLayer, feature):
        super(agDataLoggerView, self).__init__(tLayer, feature)
        pass

    def _export(self):
        pass

    def _intervalChanged(self, idx):
        pass

    def show(self):
        pass

    def _refresh(self):
        pass
    
    def _error(self, mqtt, msg=""):
        Log.warn(msg)

    def update(self, data):
        pass

class agChartView(agDataView):
    def __init__(self, tabs, tLayer, feature):
        super(dsChartView, self).__init__(tLayer, feature)
        self._tabs = tabs
        # self._tabs.btnRefreshc.setEnabled(True)


    def _intervalChanged(self, idx):
        pass

    def show(self):
        pass

    def update(self, data):
        pass

    def _refresh(self):
        pass

    def _error(self, mqtt, msg=""):
        pass


class agConfigView(QObject):
    def __init__(self, tabs, tLayer, feature,params): # change to broker?
        super(agConfigView, self).__init__()
        self._tabs = tabs
        self.pTable = None
        self._topicManager = tLayer.topicManager()
        self._params = params
        try:
            self.pTable = agParameterTable(tabs.tblParams, params)
            self._tabs.btnApply.clicked.connect(self._apply)
        except Exception as e:
            Log.debug("Error loading Configuration tab " + str(e))

    def _applied(self):
        pass

    def _apply(self):
        params = self.pTable.params()
        payload = json.dumps({topic,})
        request = "agsense/request/get"
        _client  = None
        try:
            _client = tlMqttSingleShot(self,
                                    self.tLayer.getBroker().host(),
                                    self.getBroker().port(),
                                    request,
                                    ["agsense/response/set"],
                                    payload,
                                    30)
            QObject.connect(_client, QtCore.SIGNAL("mqttOnCompletion"), self._applied)
            QObject.connect(_client, QtCore.SIGNAL("mqttConnectionError"), self._applied)
            QObject.connect(_client, QtCore.SIGNAL("mqttOnTimeout"), self._applied)
      
            _client.run()
        except Exception as e:
            Log.debug("Error requesting list of devices " + str(e))
            if _client:
                _client.kill()
  


    def show(self):
        pass

    def update(self, data):
        pass


    def _refresh(self):
        pass

    def _error(self, mqtt, msg=""):
        Log.progress(msg)


class agFeatureDialog(tlFeatureDialog):
    """
    Implementation of tlFeatureDialog.

    """

    @staticmethod
    def _createTab(Tabs, widget):
        idx = Tabs.indexOf(widget)
        return Tabs.widget(idx), Tabs.tabText(idx), idx

    def __init__(self, dialog, tLayer, feature):
        agTabs = agDataTab()
        widgets = []
        Tabs = agTabs.Tabs

        Log.debug("Checking params")   

        topic = tLayer.getBroker().topic(feature['topic'])
        params = topic['params']
        Log.debug(params)   
        

        #widgets.append(tlDsFeatureDialog._createTab(Tabs, dsTabs.dataTab))
        #widgets.append(tlDsFeatureDialog._createTab(Tabs, dsTabs.chartTab))

        if len(params) >0:
            widgets.append(agFeatureDialog._createTab(Tabs, agTabs.configTab))

        super(agFeatureDialog, self).__init__(dialog, tLayer, feature, widgets)
       # self._dataTab = dsDataLoggerView(dsTabs, tLayer, feature)
       # self._dataTab.show()
       # self._chartTab = dsChartView(dsTabs, tLayer, feature)
       # self._chartTab.show()
        if len(params) >0:
            self._configTab = agConfigView(agTabs, tLayer, feature,params)
            self._configTab.show()

        topicCombo = self._find(QComboBox, 'topic') # Disable changing topics!
        if topicCombo:
            topicCombo.setEnabled(False)
        

    