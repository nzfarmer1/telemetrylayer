# -*- coding: utf-8 -*-
"""
/***************************************************************************
 dsTopicManager
 
 DigiSense Topic Manager - needs backend DigiSense server. 

 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from tlabstracttopicmanager import tlAbstractTopicManager
from ui_dstopicmanager import Ui_dsTopicManager 
from lib.tlsettings import tlSettings as Settings, tlConstants
from lib.tllogging import tlLogging as Log
from tlmqttclient import *
from dsdevicemapdialog import dsDeviceMapDialog as DeviceMapDialog
from lib.dsdevicemaps import   dsDeviceMap as DeviceMap, dsDeviceMaps as DeviceMaps
from lib.dsdevicetypes import dsDeviceType as DeviceType, dsDeviceTypes as DeviceTypes
import os

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


class dsTopicManager(tlAbstractTopicManager, Ui_dsTopicManager):
    
    kDeviceMapsTabId     = 0
    kDeviceLogicalTabId  = 1
    kDeviceTypesTabId    = 2

    
    @staticmethod
    def showLoadingMessage(tbl,msg = _translate("dsTopicManager", "Loading data ...", None)):
        tbl.clear()
        tbl.setStyleSheet("font-style: italic;") 
        tbl.setRowCount(1)
        tbl.setShowGrid(False)
        tbl.setColumnCount(1)
        item = QtGui.QTableWidgetItem(0)
        item.setText(msg)
        item.setFlags(Qt.NoItemFlags)
        tbl.setItem(0,0,item)
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setVisible(False)
        tbl.horizontalHeader().setStretchLastSection(True)
    
    def __init__(self,broker,create=False):
        super(dsTopicManager,self).__init__(broker,create)
    
        self._tested = False
        self._deviceMaps = None
        self._deviceTypes = None
        self._create = create
        self._broker= broker
          


    def setupUi(self):
        super(dsTopicManager,self).setupUi()
       
        if self._create == True:
            self._mode = tlConstants.Create
            self.deviceTabs.setCurrentIndex(dsTopicManager.kDeviceMapsTabId); # First index
        else:
            self._mode = tlConstants.Update
            self.deviceTabs.setCurrentIndex(dsTopicManager.kDeviceLogicalTabId); # First index
     
        QObject.connect(self,SIGNAL("deviceMapsRefreshed"),self._buildDevicesTables)
        QObject.connect(self,SIGNAL("deviceMapsRefreshed"),self._updateLayers)
        
        if self._deviceTypes == None:
             Log.debug("Loading device types")  
             self.setDeviceTypes(self._loadDeviceTypes()) 
        self.devicesRefresh.clicked.connect(self._deviceMapsRefresh)
        
        dsTopicManager.showLoadingMessage( self.tableDeviceTypes)
        dsTopicManager.showLoadingMessage( self.tableLogical)
        dsTopicManager.showLoadingMessage( self.tablePhysical)
        
        self.tableLogical.doubleClicked.connect(self._editTopicRow)

        if self._deviceMaps != None:
            self._buildDevicesTables()
        else:
            self._deviceMapsRefresh()
        
        if self._deviceTypes != None:
            self._buildDeviceTypesTable()
        else:
           QObject.emit(self,QtCore.SIGNAL('topicManagerError'),False,"Unable to load device types")
           
    def _updateFeatures(self):
        # Iterate through a list of tlLayers and if they are using
        # dsTopicManager update the features with any new parameter settings
        pass
       
    def _editTopicRow(self,modelIdx):
        item = self.tableLogical.item(modelIdx.row(),0)
        self.handleButton(item.data(0))
       
        
    def __del__(self):
        self.devicesRefresh.clicked.disconnect(self._deviceMapsRefresh)
        QObject.disconnect(self,SIGNAL("deviceMapsRefreshed"),self._buildDevicesTables)
        QObject.disconnect(self,SIGNAL("deviceMapsRefreshed"),self._updateLayers)

    def getWidget(self):
        self.setupUi()
        return self.Tabs.widget(0)

    def getTopics(self):
        topics = []
        for deviceKey,device in self._deviceMaps:
            devicemap = DeviceMap.loads(device)
            if not devicemap.isMapped():
                continue
            dtype = self._deviceTypes.getDeviceTypeById(devicemap.getDeviceTypeId())
            
            # Add Type(QVariant.XXX) to Params so we now how to create feature 
            params = []
            for param in dtype.params():
                pname   = param.get('name')
                pvalue  = devicemap.getParam(pname)
                ptype   = param.find("Type").text
                params.append({'name':pname,'value':pvalue,'type':ptype})
            
                
            topics.append({'topic':devicemap.getTopic(), \
                            'name':devicemap.getName(), \
                            'units':devicemap.getUnits(), \
                            'type':dtype.op(), \
                            'io':devicemap.getIO(), \
                            'params':params})

        return super(dsTopicManager,self).getTopics(topics) # Merge System topics

            
    def getDeviceTypes(self):
        return self._deviceTypes

    def getDeviceMaps(self):
        return self._deviceMaps
    
    def setDeviceTypes(self,deviceTypes):
        self._deviceTypes = deviceTypes

    def setDeviceMaps(self,deviceMaps):
        self._deviceMaps = deviceMaps

        
    def validate(self):
        return True
        

    def _buildDeviceTypesTable(self):
        devicetypes = self.getDeviceTypes()
        
        columns = ["I/O Type","IN/OUT","Type","Model"]
        tbl = self.tableDeviceTypes
        tbl.clear()

        tbl.setStyleSheet("font: 10pt \"System\";") 
        tbl.setRowCount(len(devicetypes.values()))
        tbl.setColumnCount(len(columns))
        tbl.setColumnWidth(30,30) #?
        tbl.setHorizontalHeaderLabels(columns)
        tbl.verticalHeader().setVisible(True)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)

        row=0
        for device in devicetypes.values():
            item = QtGui.QTableWidgetItem(0)
            item.setText(device.type())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row,0,item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(device.io())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row,1,item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(device.op())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row,2,item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(device.model())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row,3,item)
            row = row+1

        tbl.resizeColumnsToContents()
        tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)


    def _buildLogicalDevicesTable(self):
        Log.debug('building logical devices')
        devicemaps = self.getDeviceMaps()
        tbl = self.tableLogical

        columns = ["Name","Topic","Type"]
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
        
        

        row=0

        for deviceKey,device in devicemaps:

            devicemap = DeviceMap.loads(device)
            if not devicemap.isMapped():
                continue

            dtype = self._deviceTypes.getDeviceTypeById(devicemap.getDeviceTypeId())
 
            tbl.setRowCount(row+1)
            #item.setFlags(Qt.ItemIsSelectable)
            item = QtGui.QLabel(devicemap.getName())
            item.setToolTip(devicemap.getTopic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row,0,item)
            item = QTableWidgetItem()
            item.setData(0,devicemap)
            tbl.setItem(row,0,item)
            

            item = QtGui.QLabel(devicemap.getTopic())
            item.setToolTip(devicemap.getTopic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row,1,item)

            item = QtGui.QLabel(dtype.op())
            item.setToolTip(devicemap.getTopic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row,2,item)

            row = row+1
        tbl.resizeColumnsToContents()   
        tbl.horizontalHeader().setStretchLastSection(True)
 

    def _buildPhysicalDevicesTable(self):
        Log.debug('building physical devices')
        columns = ["Device","Type","Pin","Map"]
        tbl = self.tablePhysical
        tbl.clear()
        tbl.setRowCount(0)
        tbl.setStyleSheet("font: 10pt \"System\";") 
        tbl.setRowCount(len(self._deviceMaps))
        tbl.setColumnCount(len(columns))
        tbl.setColumnWidth(30,30) #?
        tbl.setHorizontalHeaderLabels(columns)
        tbl.verticalHeader().setVisible(True)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)
        row=0
        for deviceKey,device in self._deviceMaps:

            devicemap = DeviceMap.loads(device)

            item = QtGui.QTableWidgetItem(0)
            item.setText(devicemap.getLoByte())
            item.setFlags(Qt.ItemIsSelectable)
            tbl.setItem(row,0,item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(devicemap.getType() + " " + devicemap.getIO())
            item.setFlags(Qt.ItemIsSelectable)
            tbl.setItem(row,1,item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(devicemap.getPin())
            item.setFlags(Qt.ItemIsSelectable)
            tbl.setItem(row,2,item)

            #item = QtGui.QTableWidgetItem(0)
            #item.setText(devicemap.getUpdated())
            #item.setFlags(Qt.ItemIsSelectable)
            #tbl.setItem(row,3,item)

            button = QtGui.QPushButton('Test', self)

            button.clicked.connect(self._callback(devicemap),3)
            if devicemap.getDeviceTypeId() != None:
                button.setText('Edit')
                button.setToolTip("Configure paramaters")
            else:
                button.setText('Map')
                button.setToolTip("Map device to a Topic and configure")
            
            tbl.setCellWidget(row,3,button)

            row = row + 1

        tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.devicesRefresh.setEnabled(True)

    # trick to setup multiple callbacks in a control loop
    def _callback(self,param):
        return lambda: self.handleButton(param)
    
    def handleButton(self,devicemap):
        deviceMapDialog = DeviceMapDialog(self,devicemap)
        result = deviceMapDialog.exec_()
        if result == 1 and deviceMapDialog.dirty:
            Log.debug("Got result " + str(result))
            self.setDeviceMaps(deviceMapDialog.getDeviceMaps())
            QObject.emit(self,QtCore.SIGNAL("deviceMapsRefreshed"))
        pass    


    def _buildDevicesTables(self):
        Log.debug("Rebuilding Physical Devices Tables")
        self._buildPhysicalDevicesTable()
        Log.debug("Rebuilding Logical Devices Tables")
        self._buildLogicalDevicesTable()
        QObject.emit(self,QtCore.SIGNAL('topicManagerReady'),True,self)


    def _buildDevicesTableCallback(self,mqClient,status,response,fu="bar"):
        self.devicesRefresh.setEnabled(True)
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor));
        if status:
            self.setDeviceMaps(DeviceMaps.decode(response))
            if self._deviceTypes != None:
                self.deviceTabs.setTabEnabled(dsTopicManager.kDeviceMapsTabId,True)
                self.deviceTabs.setTabEnabled(dsTopicManager.kDeviceLogicalTabId,True)
                self.deviceTabs.setTabEnabled(dsTopicManager.kDeviceTypesTabId,True)
            self._buildDevicesTables()
        else:
            QObject.emit(self,QtCore.SIGNAL('topicManagerError'),False,response)
            dsTopicManager.showLoadingMessage(self.tablePhysical,response)
            dsTopicManager.showLoadingMessage(self.tableLogical,response)
            Log.debug(response)



    def _deviceMapsRefresh(self):
        dsTopicManager.showLoadingMessage(self.tablePhysical)
        dsTopicManager.showLoadingMessage(self.tableLogical)
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
        self.devicesRefresh.setEnabled(False)
        Log.progress("Requesting Device Maps")
        aClient = tlMqttSingleShot(self,
                                  self._broker.host(),
                                  self._broker.port(),
                                  "/digisense/request/device/maps",
                                  "/digisense/response/device/maps")
        QObject.connect(aClient, QtCore.SIGNAL("mqttOnCompletion"), self._buildDevicesTableCallback)
        QObject.connect(aClient, QtCore.SIGNAL("mqttConnectionError"), self._deviceMapsRefreshError)
        QObject.connect(aClient, QtCore.SIGNAL("mqttOnTimeout"), self._deviceMapsRefreshError)
        aClient.run()


    def _deviceMapsRefreshError(self,mqtt,msg = ""):
        dsTopicManager.showLoadingMessage(self.tablePhysical,msg)
        dsTopicManager.showLoadingMessage(self.tableLogical,msg)
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor));
        QObject.disconnect(mqtt, QtCore.SIGNAL("mqttOnCompletion"), self._buildDevicesTableCallback)
        QObject.disconnect(mqtt, QtCore.SIGNAL("mqttConnectionError"),  self._deviceMapsRefreshError)
        QObject.disconnect(mqtt, QtCore.SIGNAL("mqttOnTimeout"),  self._deviceMapsRefreshError)
        mqtt.kill()
        self.devicesRefresh.setEnabled(True)
        QObject.emit(self,QtCore.SIGNAL('topicManagerError'),False,msg)
    
    
    def updateDeviceMap(self,map):
        pass
    
        
    def _loadDeviceTypes(self): # xml file
        
        fname = Settings.getMeta("deviceTypes")
        fullpath = os.path.join( Settings.get("plugin_dir"),fname)
        try:
                return DeviceTypes(fullpath)
        except Exception as e:
            Log.warn("Failed to load " + fullpath + str(e))
            return None
        
