# -*- coding: utf-8 -*-
"""
/***************************************************************************
 agTopicManager
 
 DigiSense Topic Manager - needs backend DigiSense server. 

 ***************************************************************************/
Todo:
Save device type parameters as attributes
Use these to create traffic lights on icon or set alerts

- In agTopicManager Update alert attribute to True of ! Appended
- Use MQTT Logo as default symbol
- Increment in lambda to scale x as [1..1024] for percentage functions
- Add iterators for DeviceTypes and DeviceMaps
- Remove call back on load
- Enabled topicManager to work in r/o mode

"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *


from TelemetryLayer.tltopicmanager import tlTopicManager, tlFeatureDialog
from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tlsettings import tlConstants as Constants
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tlmqttclient import *

from agfeaturedialog import agFeatureDialog as FeatureDialog
from ui_agtopicmanager import Ui_agTopicManager
from agdevice import agDeviceList, agDevice, agParams, agParam
    
import os, zlib, datetime, json,imp

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


class agTopicManager(tlTopicManager, Ui_agTopicManager):
    """
    Implementation of tlTopicManager
    """

    kDeviceMapsTabId = 0
    kDeviceLogicalTabId = 1
    kDeviceTypesTabId = 2

    kAlertIdx = 10


    @staticmethod
    def showLoadingMessage(tbl, msg=_translate("agTopicManager", "Loading data ...", None)):
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
        super(agTopicManager, self).__init__(broker, create)

        self._tested = False
        self._create = create
        self._broker = broker
        self._demo = False
        self._devices = None

    def setupUi(self):
        super(agTopicManager, self).setupUi()
        self._buildDevicesTable("Loading Devices")
        self._requestDevices(self._updateDevices)
        self.devicesRefresh.clicked.connect(self._requestDevices)


    def instance(self,topicType = None):
        """
        Return a possible subclassed instance of this topic manager
        Works as a dynamic factory and supports backward compatability
        For existing topic managers
        
        """
        
        if topicType is not None and topicType =='Tank':
            return agTankTopicManager(self._broker)
        return self

    def setDevices(self,devices):
        self._devices = devices

    def getDevices(self):
        return self._devices

    def featureDialog(self, dialog, tLayer, featureId):
        # Check tLayer.topicType type
        if tLayer.topicType() == 'Tank':
            return FeatureDialog(dialog, tLayer, featureId)
        else:
            return super(agTopicManager, self).featureDialog(dialog, tLayer, featureId) 


    def _updateDevices(self, mqtt, status = True, msg = None):
        if not status:
            Log.warn(msg)
            return
        Log.debug("Updating Devices")
        Log.debug(msg.payload)
        self._devices = agDeviceList(msg.payload)
        self._buildDevicesTable()

    def _requestDevices(self,callback):
        request = "agsense/request/list"
        _client  = None
        try:
            _client = tlMqttSingleShot(self,
                                    self._broker.host(),
                                    self._broker.port(),
                                    # "/digisense/request/data/10000/1",
                                    request,
                                    ["agsense/response/list"],
                                    "",
                                    30,
                                    0,
                                    callback)

            Log.progress("Requesting devices list")
            _client.run()
        except Exception as e:
            Log.debug("Error requesting list of devices " + str(e))
            if _client:
                _client.kill()


    def isDemo(self):
        return False;# self._demo

    def _updateFeatures(self):
        # Iterate through a list of tlLayers and if they are using
        # agTopicManager update the features with any new parameter settings
        pass

    def _editTopicRow(self, modelIdx):
        item = self.tableLogical.item(modelIdx.row(), 0)
        self._handleUpdateButton(item.data(0))

    def getWidget(self):
        self.setupUi()
        return self.Tabs.widget(0)

    def getTopics(self):
        topics = []
        for device in self.getDevices():
            
            topics.append({'name' :device.name(),
                           'topic':device.topic(),
                           'units':device.units(),
                           'type' :device.op(),
                           'params':device.params().dump()})
        Log.debug(json.dumps(topics))    
        return super(agTopicManager, self).getTopics(topics)  # Merge System topics

    def getBroker(self):
        return self._broker

    # Add Alert flag
    
    def beforeCommit(self,tLayer,topicType,values):
        """
        values is a dict of values to be committed
        the key is a tuple of feature Id and attribute Index
        We implement alerts by checking if the payload value
        contains a '!'. Crude but simple - no additional messages.
        
        """
        pass

    def validate(self):
        return True

        


    def _buildDevicesTable(self,msg  = ""):
        devices = self.getDevices()
        tbl = self.tableDevices

        tbl.clear()
        tbl.setRowCount(0)
        tbl.setStyleSheet("font: 10pt \"System\";")
        tbl.verticalHeader().setVisible(True)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)

        row = 0

        if not devices:
            columns = ["Device List"];
            tbl.setColumnCount(len(columns))
            tbl.setHorizontalHeaderLabels(columns)
            tbl.setRowCount(row + 1)
            if msg:
                item = QtGui.QLabel(msg)
                item.setToolTip(msg)
            else:
                item = QtGui.QLabel("No Devices Available")
                item.setToolTip("No Devices Available -  Please check your settings")
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 0, item)
            tbl.resizeColumnsToContents()
            tbl.horizontalHeader().setStretchLastSection(True)
            return

        columns = ["Type", "Name", "Topic"]
        tbl.setColumnCount(len(columns))
        tbl.setHorizontalHeaderLabels(columns)

        for device in devices:

            tbl.setRowCount(row + 1)

            item = QtGui.QLabel(device.op())
            item.setToolTip(device.topic()) # Add description
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 0, item)
            item = QTableWidgetItem()
            item.setData(0, device)
            tbl.setItem(row, 0, item)

            item = QtGui.QLabel(device.name())
            item.setToolTip(device.topic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 1, item)

            item = QtGui.QLabel(device.topic())
            item.setToolTip(device.topic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 2, item)

            row += 1
        tbl.resizeColumnsToContents()
        tbl.horizontalHeader().setStretchLastSection(True)


    def getAttributes(self, topicType):
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


    @staticmethod
    def register():
        Log.debug("Generic Register")

        path = os.path.join(os.path.dirname(__file__), 'qgsfuncs.py')
        imp.load_source('qgsfuncs', path)

        # from qgsfuncs import format_label
        pass


    @staticmethod
    def unregister():
        if QgsExpression.isFunctionName("$format_label"):
            QgsExpression.unregisterFunction("$format_label")

    def __del__(self):
        QObject.disconnect(self, SIGNAL("deviceMapsRefreshed"), self._buildDevicesTables)


    
class agTankTopicManager(agTopicManager, Ui_agTopicManager):
    def __init__(self, broker):
        super(agTopicManager, self).__init__(broker, False)
        self._broker = broker
        pass

    def setLabelFormatter(self, layer, topicType):
        try:
            palyr = QgsPalLayerSettings()
            palyr.readFromLayer(layer)
            palyr.enabled = True
            palyr.placement = QgsPalLayerSettings.OverPoint
            palyr.quadOffset = QgsPalLayerSettings.QuadrantBelow
            palyr.yOffset = 0.01
            palyr.fieldName = '$agsense_format_label'
            palyr.writeToLayer(layer)
        except Exception as e:
            Log.debug("Error setting Format " + str(e))
