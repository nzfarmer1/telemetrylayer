# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DigiSenseDeviceMappingDialog
 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from TelemetryLayer.lib.tlsettings import tlSettings as Settings, tlConstants
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tlmqttclient import *

from ui_dsdevicemapdialog import Ui_dsDeviceMapDialog
from dsdevicemaps import dsDeviceMap as DeviceMap, dsDeviceMaps as DeviceMaps
from dsdevicetypes import dsDeviceType as DeviceType, dsDeviceTypes as DeviceTypes
from dsrpcproxy import dsRPCProxy as RPCProxy

import traceback, sys


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
            self.name = param.get('name')
            self.title = param.get('title')
            self.tooltip = param.get('description')
            self.type = param.find('Type').text
            if default is None:
                try:
                    self.default = param.find('Default').text
                except:
                    self.default = 1
            else:
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
            self.min = param.find('Min').text
            self.max = param.find('Max').text
            self.int = param.find('Interval').text
            self.units = param.find('Units').text
            try:
                self.step = param.find('Step').text
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
            self.min = param.find('Min').text
            self.max = param.find('Max').text
            self.int = param.find('Interval').text
            self.units = param.find('Units').text
            try:
                self.step = param.find('Step').text
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
        for option in param.find('Options'):
            self.control.insertItem(idx, option.text, option)
            if option.get('value') == self.default:
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


class dsParameterTable(QObject):
    _params = []

    def __init__(self, deviceMap, deviceType, tableWidget, mode):
        super(dsParameterTable, self).__init__()

        tblParam = tableWidget
        self._mode = mode
        self._deviceMap = deviceMap
        tblParam.horizontalHeader().setVisible(False)
        tblParam.verticalHeader().setVisible(False)

        del self._params[:]

        tblParam.clearContents()
        tblParam.setRowCount(0)
        tblParam.setShowGrid(True)
        tblParam.setColumnCount(2)
        Log.debug("Param Table " + str(deviceType))

        if deviceType is None:
            return

        _params = deviceType.params()
        if _params is None or len(_params) == 0:
            return

        # Create a table of controls preset with existing values if required
        # Parameters are defined in the device maps XML

        for param in _params:
            default = None
            if self._mode == tlConstants.Update:
                default = self._deviceMap.getParam(param.get('name'))

            if param.get('widget') == 'slider':
                self._params.append(tlTableParamSlider(tblParam, tblParam.rowCount(), param, default))
            if param.get('widget') == 'select':
                self._params.append(tlTableParamCombo(tblParam, tblParam.rowCount(), param, default))
            if param.get('widget') == 'spinbox':
                self._params.append(tlTableParamSpinBox(tblParam, tblParam.rowCount(), param, default))

    def params(self):
        params = {}
        for param in self._params:
            # Log.debug("Setting " + param.getName() + " to " + str(param.getValue()))
            params[param.getName()] = param.getValue()

        return params


# Class to handle mapping of physical with a logical device
# Mappings are currently 1<=>1

class dsDeviceMapDialog(QtGui.QDialog, Ui_dsDeviceMapDialog):
    def __init__(self, creator, devicemap=None):
        super(dsDeviceMapDialog, self).__init__()
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self._creator = creator
        self._broker = creator._broker
        self._deviceMap = devicemap
        self._deviceTypes = None
        self._curDeviceIdx = None
        self.params = []
        self.mode = tlConstants.Create  # By default we are in create mode
        self.dirty = False
        self.paramTable = None

        self.setupUi()
        pass

    def setupUi(self):
        super(dsDeviceMapDialog, self).setupUi(self)
        try:
            self._deviceTypes = self._creator.getDeviceTypes()
            self._devicesMaps = self._creator.getDeviceMapsRPC()
            Log.debug("Device Key = " + self._deviceMap.getDeviceKey())
            self.deviceKeyLabel.setText(self._deviceMap.getDeviceKey())
            self.deviceKeyLabel.setToolTip(self._deviceMap.getDeviceKey())

            if self._deviceMap.getDeviceTypeId() is not None and self._deviceMap.getTopic() is not None:
                self.mode = tlConstants.Update

            self.createTypesCombo(self._deviceMap.getDeviceTypeId())
            self.applyButton.clicked.connect(self.validateApplyRPC)

            # if self._creator.isDemo():
            #    Log.progress("Demo mode - no changes can be applied")
            #    self.applyButton.setEnabled(False)

            noSpaceValidator = QRegExpValidator(QRegExp("^[\$A-Za-z0-9\/]+"), self)
            self.topic.setValidator(noSpaceValidator)
            self.topic.setReadOnly(True)
            if self._deviceMap.getTopic() is not None:
                self.topic.setText(self._deviceMap.getTopic())

            spaceValidator = QRegExpValidator(QRegExp("^[a-zA-Z0-9 ]+"), self)
            self.name.setValidator(spaceValidator)
            if self._deviceMap.getName() is not None:
                self.name.setText(self._deviceMap.getName())

            if self.mode == tlConstants.Create:
                self.name.textEdited.connect(self.nameChanged)
                self.deleteButton.hide()
            elif self.mode == tlConstants.Update:
                self.topic.setDisabled(True)
                self.deviceType.setDisabled(True)
                self.deleteButton.clicked.connect(self.validateDeleteRPC)


        except Exception as e:
            Log.warn("Error loading catalog of Device Types " + str(e))

    # Create Dropdown of the Device Type Catalog

    def createTypesCombo(self, deviceTypeId=None):
        self.deviceType.addItem('Unspecified', None)

        idx = 1  # After adding empty index
        for dtype in self._deviceTypes.values():
            try:
                if dtype.type() != self._deviceMap.getType():
                    continue
                # Add type to drop down
                self.deviceType.addItem(
                    dtype.op() + ' (' + dtype.find('Manufacturer') + ' ' + dtype.find('Model') + ')', dtype)

                if deviceTypeId is not None and dtype.id() == deviceTypeId:
                    self.deviceType.setCurrentIndex(idx)

                idx += 1
            except Exception as e:
                Log.warn(dtype.id() + " " + str(e))

            self.deviceType.currentIndexChanged.connect(self.deviceTypeIndexChanged)
            self.deviceTypeIndexChanged(self.deviceType.currentIndex())

    def nameChanged(self, _str):
        replacement = '/digisense/maps/' + _str.lower().replace(' ', '/')
        self.topic.setText(replacement)

    def deviceTypeIndexChanged(self, i):
        self.applyButton.setDisabled(i == 0)
        if i == 0:
            return
        if self._curDeviceIdx != self.deviceType.itemData(i):
            self._curDeviceIdx = self.deviceType.itemData(i)
            self.paramTable = dsParameterTable(self._deviceMap, self._curDeviceIdx, self.parameterTable, self.mode)


        # Validate deletion of a Device Map

    def validateDeleteRPC(self, status):
        if self._creator.isDemo():
            Log.progress("Demo mode - no changes can be applied")
            self.dirty = False
            self.accept()
            return

        msg = "Are you sure you want to delete this mapping?  Please note you will need to edit/delete any features that use this Topic"
        if not Log.confirm(msg):
            return

        try:
            s = RPCProxy(self._broker.host(), 8000).connect()
            Log.debug(self._deviceMap.dumps())
            if s.delMap(str(self._deviceMap.getTopic())):
                Log.progress("Device map deleted")
                self.dirty = True
                self.accept()
            else:
                Log.critical("There was an error deleting this device map")
            self.mode = tlConstants.Deleted
        except:
            Log.debug("Error deleting map: " + str(e))

    # Apply changes to individual map



    def validateApplyRPC(self, status):
        Log.debug("Apply RPC")
        if self._creator.isDemo():
            Log.progress("Demo mode - no changes can be applied")
            self.dirty = False
            self.accept()
            return

        if len(self.name.text()) < 4:
            Log.alert("Please ensure the name is at least 4 characters long")
            return

        try:
            Log.debug(self.paramTable)
            params = self.paramTable.params()
            dtype = self.deviceType.itemData(self.deviceType.currentIndex())
            self._deviceMap.setDeviceTypeId(dtype.id())
            self._deviceMap.set('name', self.name.text())
            self._deviceMap.set('topic', self.topic.text())
            self._deviceMap.set('manufacturer', dtype.manufacturer())
            self._deviceMap.set('model', dtype.model())
            self._deviceMap.set('units', dtype.units())
            self._deviceMap.set('params', params)
            s = RPCProxy(self._broker.host(), 8000).connect()
            if s.setMap(self._deviceMap.dumps()):
                Log.progress("Device map updated")
                self.dirty = True
                self.accept()
            else:
                Log.critical("There was an error updating this device map")

        except Exception as e:
            Log.debug("Error saving map " + str(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.debug(repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback)))


    def mapsReloaded(self):
        Log.alert("Device information updated.")
        if self.mode == tlConstants.Deleted:
            self.accept()
            return
        self.applyButton.setDisabled(False)


    def __del__(self):
        del self.params[:]
        pass

