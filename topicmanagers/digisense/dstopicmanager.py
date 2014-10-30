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

from TelemetryLayer.tltopicmanager import tlTopicManager, tlFeatureDialog
from TelemetryLayer.lib.tlsettings import tlSettings as Settings, tlConstants
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tlmqttclient import *

from ui_dstopicmanager import Ui_dsTopicManager
from ui_dsdatatabwidget import Ui_Form

from dsdevicemapdialog import dsDeviceMapDialog as DeviceMapDialog
from dsdevicemaps import   dsDeviceMap as DeviceMap, dsDeviceMaps as DeviceMaps
from dsdevicetypes import dsDeviceType as DeviceType, dsDeviceTypes as DeviceTypes

import os,zlib, datetime, json

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

deviceTypesPath  =""

class dsDataTab(QDialog, Ui_Form):

    def __init__(self):
        Log.debug("Init form")
        try:
            super(dsDataTab,self).__init__()
            self.setupUi(self)
        except Exception as e:
            Log.debug(e)


class dsDataView(QObject):

    def __init__(self,tLayer,feature):
        super(dsDataView,self).__init__()
        self._tlayer = tLayer
        self._feature = feature
        self._client = None
        pass

    @staticmethod
    def _intervals():
        return [['Tick',[(1,60,'1 Hour'),(1,120,'2 Hours'),(1,180,'3 Hours'),(1,240,'4 Hours'),(1,300,'5 Hours'),(1,360,'6 Hours'),(1,720,'12 Hours'),(1,1440,'24 Hours')]],
                ['1 Minute',[(60,1440,'1 Day'),(60,2880,'2 Days'),(60,7200,'5 Days'),(60,14400,'10 Days')]],
                ['15 Minutes',[(900,960,'10 Days')]]]

    def _request(self,interval,duration):
        publish = "/digisense/request/data/" + str(interval*duration) + "/" + str(interval)
        try:
            self._client = tlMqttSingleShot(self,
                                        self._tlayer.host(),
                                        self._tlayer.port(),
                                        #"/digisense/request/data/10000/1",
                                        publish,
                                        ["/digisense/response/data" + self._feature['topic'] , "/digisense/response/data" + self._feature['topic'] + "/compressed"],
                                        self._feature['topic'],
                                        30)
            QObject.connect(self._client, QtCore.SIGNAL("mqttOnCompletion"), self._update)
            QObject.connect(self._client, QtCore.SIGNAL("mqttConnectionError"), self._error)
            QObject.connect(self._client, QtCore.SIGNAL("mqttOnTimeout"),  self._error)

            Log.progress("Requesting data for " + str( self._feature['topic'] ))    
            self._client.run()
        except Exception:
            Log.debug("Data Logger ")
            self._client.kill()

class dsDataLoggerView(dsDataView):

    def __init__(self,dataTab,tLayer,feature):
        super(dsDataLoggerView,self).__init__(tLayer,feature)
        self._dataTab = dataTab
        self._dataTable = dataTab.tableWidget
        
        for (name,durations) in self._intervals():
            self._dataTab.selectInterval.addItem(name,durations)
            if name == 'Tick':
                for (interval,duration,name) in durations:
                    self._dataTab.selectDuration.addItem(name,(interval,duration) )
        
        self._dataTab.btnRefresh.clicked.connect(self._refresh)
        self._dataTab.btnExport.clicked.connect(self._export)
        self._dataTab.selectInterval.currentIndexChanged.connect(self._intervalChanged)


           
    
    def _export(self):
            fileName = QFileDialog.getSaveFileName(None, "Location for export (.csv) File",
              "~/",
              "*.csv")
            if not fileName:
                return
            try:
                qfile = QFile(fileName)
                qfile.open(QIODevice.WriteOnly)
                for row in self._dataTable.rowCount():
                    x = self._dataTable.item(row,0).text()
                    y = self._dataTable.item(row,1).text()
                    QTextStream(qfile) << str(x) + "," + str(y) + "\n"
                qfile.flush()
                qfile.close()
            except Exception as e:
                Log.alert(str(e))

           
    def _intervalChanged(self,idx):
        durations = self._dataTab.selectInterval.itemData(idx)
        self._dataTab.selectDuration.clear()
        for (interval,duration,name) in durations:
            self._dataTab.selectDuration.addItem(name,(interval,duration) )

    def show(self):
        self._dataTab.btnExport.setEnabled(False)
        columns = ["Time","Value"]
        tbl = self._dataTable
        tbl.clear()

        tbl.setStyleSheet("font: 10pt \"System\";") 
        tbl.setRowCount(0)
        tbl.setColumnCount(len(columns))
        tbl.setColumnWidth(30,30) #?
        tbl.setHorizontalHeaderLabels(columns)
       # tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)
        tbl.setSortingEnabled(True)

        tbl.resizeColumnsToContents()
        tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        pass

    def _refresh(self):
        (interval,duration)  = self._dataTab.selectDuration.itemData(self._dataTab.selectDuration.currentIndex())
        self._request(interval,duration)
        self._dataTab.btnRefresh.setEnabled(False)

    def _error(self,mqtt,msg = ""):
        
        self._dataTab.btnRefresh.setEnabled(True)
        Log.warn(msg)
        

    def _update(self,client,status,msg):

#        del self._client
        self._dataTab.btnRefresh.setEnabled(True)

        if not status:
            Log.alert(msg)
            return
        
        tbl = self._dataTable

        try:
            tbl.setRowCount(0)
            if 'compressed' in msg.topic:
                response = json.loads(zlib.decompress(msg.payload))
            else:
                response = json.loads(msg.payload)

            if response['warn'] == '1':
                Log.progress(response['warning'])
    
            records = response['records']
            if records < 1:
                Log.progress("Nothing returned")
            
            data    = response['data']
    
            row=0
            for (x,y) in list(data):
                d =  datetime.datetime.fromtimestamp(x)
    
                tbl.setRowCount(row+1)
                item = QtGui.QTableWidgetItem(0)
                item.setText(d.strftime("%Y-%m-%d %H:%M:%S"))
                item.setFlags(Qt.NoItemFlags)
                tbl.setItem(row,0,item)
    
                item = QtGui.QTableWidgetItem(0)
                #item.setText(d.strftime("%y-%m-%d-%H:%M:%S"))
                item.setText(str(y))
                item.setFlags(Qt.NoItemFlags)
                tbl.setItem(row,1,item)
    
                row = row+1
            tbl.resizeColumnsToContents()
            tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        except Exception as e:
            Log.debug(e)
        finally:
            self._dataTab.btnExport.setEnabled(tbl.rowCount() > 0 )



class tlDsFeatureDialog(tlFeatureDialog):
    
    def __init__(self,dialog,tLayer,feature):
        dsTabs = dsDataTab()
        Tabs = dsTabs.Tabs
        idx = Tabs.indexOf(dsTabs.dataTab)
        super(tlDsFeatureDialog,self).__init__(dialog,tLayer,feature,Tabs,[idx])
        self._dataTab = dsDataLoggerView(dsTabs,tLayer,feature)
        self._dataTab.show()
    


class dsTopicManager(tlTopicManager, Ui_dsTopicManager):
    
    kDeviceMapsTabId     = 0
    kDeviceLogicalTabId  = 1
    kDeviceTypesTabId    = 2
    kDevicesFile         = "dsdevices.xml"
     
    
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
        print deviceTypesPath
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
#        QObject.connect(self,SIGNAL("deviceMapsRefreshed"),self._updateLayers)
        
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


    def featureDialog(self,dialog,tLayer,featureId): # Check SYS type?
         return tlDsFeatureDialog(dialog,tLayer,featureId)

           
    def _updateFeatures(self):
        # Iterate through a list of tlLayers and if they are using
        # dsTopicManager update the features with any new parameter settings
        pass
       
    def _editTopicRow(self,modelIdx):
        item = self.tableLogical.item(modelIdx.row(),0)
        self.handleButton(item.data(0))
       
        
    def __del__(self):
        if hasattr(self,'devicesRefresh'):
            self.devicesRefresh.clicked.disconnect(self._deviceMapsRefresh)
        QObject.disconnect(self,SIGNAL("deviceMapsRefreshed"),self._buildDevicesTables)
#        QObject.disconnect(self,SIGNAL("deviceMapsRefreshed"),self._updateLayers)

    def getWidget(self):
        self.setupUi()
        return self.Tabs.widget(0)

    def getTopics(self):
        topics = []
        if  self._deviceMaps == None:
            return []
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
                            'params':params})
        Log.debug(topics)
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
        
        columns = ["Pin Type","Sensor Type","Model"]
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
            item.setText(device.type().upper())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row,0,item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(device.op())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row,1,item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(device.model())
            item.setFlags(Qt.NoItemFlags)
            tbl.setItem(row,2,item)
            row = row+1

        tbl.resizeColumnsToContents()
        tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)


    def _buildLogicalDevicesTable(self):
        Log.debug('building logical devices')
        devicemaps = self.getDeviceMaps()
        tbl = self.tableLogical

        columns = ["Type","Name","Topic"]
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

            item = QtGui.QLabel(dtype.op())
            item.setToolTip(devicemap.getTopic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row,0,item)
            item = QTableWidgetItem()
            item.setData(0,devicemap)
            tbl.setItem(row,0,item)

            #item.setFlags(Qt.ItemIsSelectable)
            item = QtGui.QLabel(devicemap.getName())
            item.setToolTip(devicemap.getTopic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row,1,item)

            item = QtGui.QLabel(devicemap.getTopic())
            item.setToolTip(devicemap.getTopic())
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row,2,item)

            row = row+1

        tbl.resizeColumnsToContents()   
        tbl.horizontalHeader().setStretchLastSection(True)
        
 

    def _buildPhysicalDevicesTable(self):
        Log.debug('building physical devices')
        columns = ["Address (Hi)","Type","Pin","Map"]
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
            item.setText(devicemap.getAddrHigh())
            item.setFlags(Qt.ItemIsSelectable)
            tbl.setItem(row,0,item)

            item = QtGui.QTableWidgetItem(0)
            item.setText(devicemap.getType().upper())
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


    def _buildDevicesTableCallback(self,mqClient,status,msg,fu="bar"):
        self.devicesRefresh.setEnabled(True)
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor));
        if status:
            self.setDeviceMaps(DeviceMaps.decode(msg.payload))
            Log.debug('xxx ' + str(self._deviceTypes))
            if self._deviceTypes != None:
                self.deviceTabs.setTabEnabled(dsTopicManager.kDeviceMapsTabId,True)
                self.deviceTabs.setTabEnabled(dsTopicManager.kDeviceLogicalTabId,True)
                self.deviceTabs.setTabEnabled(dsTopicManager.kDeviceTypesTabId,True)
                self._buildDevicesTables()
        else:
            QObject.emit(self,QtCore.SIGNAL('topicManagerError'),False,msg.payload)
            dsTopicManager.showLoadingMessage(self.tablePhysical,msg.payload)
            dsTopicManager.showLoadingMessage(self.tableLogical,msg.payload)



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
                                  ["/digisense/response/device/maps"])
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
        try:
            return DeviceTypes(os.path.join(self.path(),dsTopicManager.kDevicesFile))
        except Exception as e:
            Log.warn("Failed to load "  + str(e))
            return None
        

    def setLabelFormatter(self,layer,topicType):
        Log.debug( str(self) + " setFormatter")
        try:
            palyr = QgsPalLayerSettings()
            palyr.readFromLayer(layer)
            palyr.enabled       = True 
            palyr.placement     = QgsPalLayerSettings.OverPoint
            palyr.quadOffset    = QgsPalLayerSettings.QuadrantBelow 
            palyr.yOffset       = 0.01
            palyr.fieldName     = '$format_label'
            palyr.writeToLayer(layer)
        except Exception as e:
            Log.debug("Error setting Format " + str(e))
            
    def setLayerStyle(self,layer,topicType):
            if not self.path() in QgsApplication.svgPaths():
                QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [self.path()])
            self.loadStyle(layer,os.path.join(self.path(),"rules.qml"))
            
            
        
