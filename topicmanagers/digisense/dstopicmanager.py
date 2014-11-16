# -*- coding: utf-8 -*-
"""
/***************************************************************************
 dsTopicManager
 
 DigiSense Topic Manager - needs backend DigiSense server. 

 ***************************************************************************/
Todo:
Save device type parameters as attributes
Use these to create traffic lights on icon or set alerts

"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from TelemetryLayer.tltopicmanager import tlTopicManager, tlFeatureDialog
from TelemetryLayer.lib.tlsettings import tlSettings as Settings, tlConstants
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tlmqttclient import *

from dsfeaturedialog import tlDsFeatureDialog as dsFeatureDialog, DeviceMap, DeviceMaps, DeviceType, DeviceTypes
from dsdevicemapdialog import dsDeviceMapDialog as DeviceMapDialog
from ui_dstopicmanager import Ui_dsTopicManager
from dsrpcproxy import dsRPCProxy as RPCProxy

import os, zlib, datetime, json

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

deviceTypesPath = ""


class dsTopicManager(tlTopicManager, Ui_dsTopicManager):
    """
    Implementation of tlTopicManager
    """

    kDeviceMapsTabId = 0
    kDeviceLogicalTabId = 1
    kDeviceTypesTabId = 2


    @staticmethod
    def showLoadingMessage(tbl, msg=_translate("dsTopicManager", "Loading data ...", None)):
        tbl.clear()
        tbl.setStyleSheet("font-style: italic;")
        tbl.setRowCount(1)
        tbl.setShowGrid(False)
        tbl.setColumnCount(1)
        item = QtGui.QTableWidgetItem(0)
        item.setText(msg)
        item.setFlags(Qt.NoItemFlags)
        tbl.setItem(0, 0, item)
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setVisible(False)
        tbl.horizontalHeader().setStretchLastSection(True)

    def __init__(self, broker, create=False):
        print deviceTypesPath
        super(dsTopicManager, self).__init__(broker, create)

        self._tested = False
        self._deviceMaps = None
        self._deviceTypes = None
        self._create = create
        self._broker = broker
        self._demo = False

        #try:
        #    Log.debug("Connecting RPC")
        #    s = RPCProxy(self._broker.host(), 8000).connect()
        #    self._demo = s.isDemo()
        #except socket.error as err:
        #    Log.progress("Error making connection to server " + str(err))
        #except Exception as e:
        #    Log.debug(e)


    def setupUi(self):
        super(dsTopicManager, self).setupUi()

        if self._create:
            self._mode = tlConstants.Create
            self.deviceTabs.setCurrentIndex(dsTopicManager.kDeviceMapsTabId)  # First index
        else:
            self._mode = tlConstants.Update
            self.deviceTabs.setCurrentIndex(dsTopicManager.kDeviceLogicalTabId)  # First index

        try:
            s = RPCProxy(self._broker.host(), 8000).connect()
            self._demo = s.isDemo()
        except socket.error as err:
            QObject.emit(self, QtCore.SIGNAL('topicManagerError'), False,
                         "Unable to load Topic Manager Digisense:" + str(err))
            return
        except Exception as e:
            Log.debug("setupUI " + str(e))
            QObject.emit(self, QtCore.SIGNAL('topicManagerError'), False,
                         "Unable to load Topic Manager Digisense:" + str(e))
            return

        self._buildDevicesTables()
        self.devicesRefresh.clicked.connect(self._deviceMapsRefreshRPC)
        self.tableLogical.doubleClicked.connect(self._editTopicRow)


    def featureDialog(self, dialog, tLayer, featureId):
        # Check tLayer.topicType type
        if tLayer.topicType() == 'Tank':
            return dsFeatureDialog(dialog, tLayer, featureId)
        else:
            return super(dsTopicManager, self).featureDialog(dialog, tLayer, featureId) 


    def isDemo(self):
        return self._demo

    def _updateFeatures(self):
        # Iterate through a list of tlLayers and if they are using
        # dsTopicManager update the features with any new parameter settings
        pass

    def _editTopicRow(self, modelIdx):
        item = self.tableLogical.item(modelIdx.row(), 0)
        self.handleButton(item.data(0))

    def getWidget(self):
        self.setupUi()
        return self.Tabs.widget(0)

    def getTopics(self):
        Log.debug("GET TOPICS")
        topics = []
        if self._deviceMaps is None:
            return []
        for deviceKey, device in self._deviceMaps:
            devicemap = DeviceMap.loads(device)
            if not devicemap.isMapped():
                continue
            dtype = self.getDeviceType(devicemap)

            # Add Type(QVariant.XXX) to Params so we now how to create feature 
            params = []
            for param in dtype.params():
                pname = param.get('name')
                pvalue = devicemap.getParam(pname)
                ptype = param.find("Type").text
                params.append({'name': pname, 'value': pvalue, 'type': ptype})

            topics.append({'topic': devicemap.getTopic(),
                           'name': devicemap.getName(),
                           'units': devicemap.getUnits(),
                           'type': dtype.op(),
                           'params': params})

        return super(dsTopicManager, self).getTopics(topics)  # Merge System topics

    def getDeviceType(self, dMap):
        return self.getDeviceTypes().getDeviceTypeById(dMap.getDeviceTypeId())

    def getDeviceTypes(self):
        if not self._deviceTypes:
            self._deviceTypes = self._loadDeviceTypesRPC()
        return self._deviceTypes

    def getDeviceMaps(self, refresh=False):
        if self._deviceMaps and not refresh:
            return self._deviceMaps
        try:
            Log.debug("Refreshing Device Maps")
            s = RPCProxy(self._broker.host(), 8000).connect()
            self._deviceMaps = DeviceMaps().decode(s.getDeviceMaps())
        except Exception as e:
            Log.progress("Error loading device maps from server")
        finally:
            if not self._deviceMaps:
                return []
            return self._deviceMaps

    def getDeviceMap(self, topic):
        d = None
        for deviceKey, device in self.getDeviceMaps():
            d = DeviceMap.loads(device)
            if d.getTopic() == topic:
                dMap = d
                break
        Log.debug(d)
        return d

    def getBroker(self):
        return self._broker


    def setDeviceTypes(self, deviceTypes):
        self._deviceTypes = deviceTypes

    def setDeviceMaps(self, deviceMaps):
        self._deviceMaps = deviceMaps


    def setDeviceMap(self, deviceMap):
        try:
            s = RPCProxy(self._broker.host(), 8000).connect()
            if s.setMap(deviceMap.dumps()):
                Log.progress("Device map updated")
                self.dirty = True
                self.accept()
            else:
                Log.critical("There was an error updating this device map")
        except Exception as e:
            Log.critical("There was an error updating this device map " + str(e))

    def validate(self):
        return True


    def _buildLogicalDevicesTable(self):
        Log.debug('building logical devices')
        devicemaps = self.getDeviceMaps()
        tbl = self.tableLogical

        columns = ["Type", "Name", "Topic"]
        tbl.clear()
        tbl.setRowCount(0)
        tbl.setStyleSheet("font: 10pt \"System\";")
        tbl.setColumnCount(len(columns))
        tbl.setHorizontalHeaderLabels(columns)
        tbl.verticalHeader().setVisible(True)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)

        row = 0

        for deviceKey, device in devicemaps:

            devicemap = DeviceMap.loads(device)
            if not devicemap.isMapped():
                continue

            dtype = self.getDeviceTypes().getDeviceTypeById(devicemap.getDeviceTypeId())

            tbl.setRowCount(row + 1)

            item = QtGui.QLabel(dtype.op())
            item.setToolTip(devicemap.getTopic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 0, item)
            item = QTableWidgetItem()
            item.setData(0, devicemap)
            tbl.setItem(row, 0, item)

            # item.setFlags(Qt.ItemIsSelectable)
            item = QtGui.QLabel(devicemap.getName())
            item.setToolTip(devicemap.getTopic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 1, item)

            item = QtGui.QLabel(devicemap.getTopic())
            item.setToolTip(devicemap.getTopic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 2, item)

            row += 1

        tbl.resizeColumnsToContents()
        tbl.horizontalHeader().setStretchLastSection(True)


    def _buildPhysicalDevicesTable(self):
        Log.debug('building physical devices')
        columns = ["Address (Hi)", "Type", "Pin", "Map"]
        tbl = self.tablePhysical
        tbl.clear()
        tbl.setRowCount(0)
        tbl.setStyleSheet("font: 10pt \"System\";")
        tbl.setRowCount(len(self.getDeviceMaps()))
        tbl.setColumnCount(len(columns))
        tbl.setColumnWidth(30, 30)  # ?
        tbl.setHorizontalHeaderLabels(columns)
        tbl.verticalHeader().setVisible(True)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)
        row = 0
        for deviceKey, device in self.getDeviceMaps():

            devicemap = DeviceMap.loads(device)

            addrHigh = devicemap.getAddrHigh()
            # addrHigh = addrHigh.replace(' ','-')

            item = QtGui.QTableWidgetItem(0)
            item.setText(addrHigh)
            item.setFlags(Qt.ItemIsSelectable)
            tbl.setItem(row, 0, item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(devicemap.getType().upper())
            item.setFlags(Qt.ItemIsSelectable)
            tbl.setItem(row, 1, item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(devicemap.getPin())
            item.setFlags(Qt.ItemIsSelectable)
            tbl.setItem(row, 2, item)

            #item = QtGui.QTableWidgetItem(0)
            #item.setText(devicemap.getUpdated())
            #item.setFlags(Qt.ItemIsSelectable)
            #tbl.setItem(row,3,item)

            button = QtGui.QPushButton('Test', self)

            button.clicked.connect(self._callback(devicemap), 3)
            if devicemap.getDeviceTypeId() is not None:
                button.setText('Edit')
                button.setToolTip("Configure paramaters")
            else:
                button.setText('Map')
                button.setToolTip("Map device to a Topic and configure")

            tbl.setCellWidget(row, 3, button)

            row += 1

        tbl.setColumnWidth(0, 80)
        tbl.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        tbl.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
        tbl.setColumnWidth(4, 55)
        self.devicesRefresh.setEnabled(True)

    # trick to setup multiple callbacks in a control loop
    def _callback(self, param):
        return lambda: self.handleButton(param)

    def handleButton(self, devicemap):
        deviceMapDialog = DeviceMapDialog(self, devicemap)
        result = deviceMapDialog.exec_()
        if result == 1 and deviceMapDialog.dirty:
            Log.debug("Got result " + str(result))
            self._deviceMapsRefreshRPC()
        pass


    def _buildDeviceTypesTable(self):
        devicetypes = self.getDeviceTypes()
        if not devicetypes:
            return

        columns = ["Pin Type", "Sensor Type", "Model"]
        tbl = self.tableDeviceTypes
        tbl.clear()

        tbl.setStyleSheet("font: 10pt \"System\";")
        tbl.setRowCount(len(devicetypes.values()))
        tbl.setColumnCount(len(columns))
        tbl.setColumnWidth(30, 30)  # ?
        tbl.setHorizontalHeaderLabels(columns)
        tbl.verticalHeader().setVisible(True)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)

        row = 0
        for device in devicetypes.values():
            item = QtGui.QTableWidgetItem(0)
            item.setText(device.type().upper())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row, 0, item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(device.op())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row, 1, item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(device.model())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row, 2, item)
            row += 1

        tbl.resizeColumnsToContents()
        tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def _buildDevicesTables(self):
        Log.debug("Rebuilding Physical Devices Tables")
        self._buildPhysicalDevicesTable()
        Log.debug("Rebuilding Logical Devices Tables")
        self._buildLogicalDevicesTable()
        self._buildDeviceTypesTable()
        QObject.emit(self, QtCore.SIGNAL('topicManagerReady'), True, self)

    def _deviceMapsRefreshRPC(self):
        try:
            deviceMaps = self.getDeviceMaps(True)

            self.setDeviceMaps(DeviceMaps.decode(deviceMaps))
            self.deviceTabs.setTabEnabled(dsTopicManager.kDeviceMapsTabId, True)
            self.deviceTabs.setTabEnabled(dsTopicManager.kDeviceLogicalTabId, True)
            self.deviceTabs.setTabEnabled(dsTopicManager.kDeviceTypesTabId, True)
            self._buildDevicesTables()

            QObject.emit(self, QtCore.SIGNAL("deviceMapsRefreshed"))
        except Exception as e:  # Check for socket error!
            Log.progress("Unable to load device maps " + str(e))

    def updateDeviceMap(self, map):
        pass

    def _loadDeviceTypesRPC(self):  # xml file
        try:
            s = RPCProxy(self._broker.host(), 8000).connect()
            return DeviceTypes(s.getDeviceTypesRPC())

        except Exception as e:
            Log.progress("Error accessing server")
            return None


    def getAttributes(self, layer, topicType):
        attributes = []
        if topicType == 'Tank':  # Consider adding an <Alerts><Alert .. tag(s) each with their own lamda functions
            attributes = [QgsField("alert", QVariant.Int, "Alert", 0, 0, "Low water alert level")]

        return attributes

    def setLabelFormatter(self, layer, topicType):
        try:
            palyr = QgsPalLayerSettings()
            palyr.readFromLayer(layer)
            palyr.enabled = True
            palyr.placement = QgsPalLayerSettings.OverPoint
            palyr.quadOffset = QgsPalLayerSettings.QuadrantBelow
            palyr.yOffset = 0.01
            palyr.fieldName = '$format_label'
            palyr.writeToLayer(layer)
        except Exception as e:
            Log.debug("Error setting Format " + str(e))

    def setLayerStyle(self, layer, topicType):
        if not self.path() in QgsApplication.svgPaths():
            QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [self.path()])
        self.loadStyle(layer, os.path.join(self.path(), "rules.qml"))

    def __del__(self):
        if hasattr(self, 'devicesRefresh'):
            self.devicesRefresh.clicked.disconnect(self._deviceMapsRefreshRPC)
        QObject.disconnect(self, SIGNAL("deviceMapsRefreshed"), self._buildDevicesTables)

    