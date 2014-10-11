# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlBrokerConfig
 
 Configure individual Brokers
 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import webbrowser


from ui_tlbrokerconfig import Ui_tlBrokerConfig
from tlbrokers import tlBrokers as Brokers
from lib.tlsettings import tlSettings as Settings, tlConstants
from lib.tllogging import tlLogging as Log
from tlmqttclient import *
from tltopicmanagerfactory import tlTopicManagerFactory as topicManagerFactory
import traceback, sys,os,imp, json


# Todo
# Add Help Button


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


class tlBrokerConfig(QtGui.QDialog, Ui_tlBrokerConfig):
    
    kBrokerConfigTabId   = 0
    kFeatureListTabId    = 1
    kTopicManagerTabId   = 2
    
    def __init__(self,creator,broker,create=False):
        super(tlBrokerConfig, self).__init__()
    
        self._creator = creator
        self.plugin_dir = creator.plugin_dir
        self._iface = creator.iface
        self._layerManager = creator._layerManager
        self._create = create
        self._broker = broker
        self._topicManager = None
        self._tested = False
  
        self.setupUi()
 
    def setupUi(self):
       super(tlBrokerConfig,self).setupUi(self)

       if self._create == True:
           self._mode = tlConstants.Create
       else:
           self._mode = tlConstants.Update
    
       self.connectHelp.clicked.connect(self._help)
       self.connectTest.clicked.connect(self._test)
       
       self.connectName.setValidator(QRegExpValidator(QRegExp("^[a-zA-Z0-9\s]+"),self))
       self.connectHost.setValidator(QRegExpValidator(QRegExp("^[a-z0-9\.]+"),self))

       self.Tabs.setCurrentIndex(tlBrokerConfig.kBrokerConfigTabId); # First index
       #if Modal create mode
       self.setName(self._broker.name())
       self.setHost(self._broker.host())
       self.setPort(str(self._broker.port()))
       self.setPoll(str(self._broker.poll()))
       self.setKeepAlive(str(self._broker.keepAlive()))
       self._topicManager = None
       self._connectedTLayers = []
       self._featureListItems = {}
       self._refreshFeature = QTimer()
       self._refreshFeature.setSingleShot(True)
       self._refreshFeature.timeout.connect( self._updateFeatureList )
       self.Tabs.currentChanged.connect(lambda: self._refreshFeature.start(3))

       self.connectApply.setEnabled(False)
       self.connectTopicManager.addItem("Please select ...",None)
       
       for topicManager in topicManagerFactory.getTopicManagers():
            Log.debug(topicManager)
            self.connectTopicManager.addItem(topicManager['name'],topicManager['id'])
            
       if self._mode == tlConstants.Create: # Create Layer - so Modal
           self.connectPoll.setCurrentIndex(
           self.connectPoll.findText(Settings.get('mqttPoll',5)))
           self.connectApply.setText(_translate("tlBrokerConfig", "Create", None))
           self.connectApply.clicked.connect(self.accept)
           self.dockWidget.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
           self.dockWidget.setWindowTitle(_translate("tlBrokerConfig", "Add Broker", None))
           #self.Tabs.setEnabled(False)
        #   self.connectFarmSenseServer.setEnabled(False)
       elif self._mode == tlConstants.Update:

           self.dockWidget.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
           self.dockWidget.setWindowTitle(_translate("tlBrokerConfig", "Configure Broker ", None) + self.getName())
           self.connectApply.setText(_translate("tlBrokerConfig", "Apply", None))
           if self._broker.topicManager() !=None:
            self.setTopicManager(self._broker.topicManager())
            if self._loadTopicManager(self.getTopicManager()):
                self.connectTopicManager.setEnabled(False)
                self._loadFeatureList()
                QgsMapLayerRegistry.instance().layersRemoved.connect(self._updateFeatureList) # change to when layer is loaded also!
                QgsProject.instance().layerLoaded.connect(self._updateFeatureList)
                self.tableFeatureList.doubleClicked.connect(self._showFeatureDialog)
           else:
             self.Tabs.setEnabled(False)


    

    def _updateFeatureListItem(self,tLayer,feature):
        if self.dockWidget.isVisible()  and self.Tabs.currentIndex() == self.kFeatureListTabId:
            _topicManager = topicManagerFactory.getTopicManager(tLayer.getBroker())
            key = (tLayer.layer().id(),feature.id())
            if not key in self._featureListItems:
                self._loadFeatureList()
            if key in self._featureListItems:
                row = self._featureListItems[key]
                item = self.tableFeatureList.cellWidget(row,3)
                if item and _topicManager:
                    item.setText(_topicManager.formatPayload(tLayer.topicType(),feature['payload']))
                
   
    def _updateFeatureList(self,fid = None):
        if self.dockWidget.isVisible()  and self.Tabs.currentIndex() == self.kFeatureListTabId:
           self._loadFeatureList()
        pass
    
    def _showFeatureDialog(self,modelIdx):
        item = self.tableFeatureList.item(modelIdx.row(),0)
        layer = item.data(0)
        feature = item.data(1)
        layer.startEditing()
        self._iface.openFeatureForm(layer, feature, True) 
        pass

    def _closedFeatureDialog(self,tLayer):
        tLayer.layer().commitChanges()
        self._updateFeatureList()
     
    # Show a list of features for the layers associated with this broker            
    def _loadFeatureList(self):
        self._featureListItems = {}

        tbl = self.tableFeatureList

        columns = ["Data","Layer","Feature","Last"]
        createMode =  tbl.rowCount() == 0
        tbl.clear()
        tbl.setRowCount(0)
        tbl.setStyleSheet("font: 10pt \"System\";") 
        tbl.setColumnCount(len(columns))
        tbl.setHorizontalHeaderLabels(columns)
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        
        lm = self._layerManager
        if lm == None:
            return

        row=0
        for lid,tLayer in self._layerManager.getTLayers().iteritems():
            _topicManager = topicManagerFactory.getTopicManager(tLayer.getBroker())

            if tLayer.getBroker().id() != self._broker.id():
                continue

            if not tLayer in self._connectedTLayers:
                # Add connections and append to connected layers
                tLayer.featureDialogClosed.connect(self._closedFeatureDialog)

                tLayer.featureUpdated.connect(self._updateFeatureList)
                tLayer.layer().featureDeleted.connect(self._updateFeatureList)
                
                self._connectedTLayers.append(tLayer)

            features = tLayer.layer().getFeatures()
            for feature in features:
                if feature.id() <=0:
                    continue
                tbl.setRowCount(row+1)
                # Append the feature
                self._featureListItems[(lid,feature.id())] = row 
                item = QTableWidgetItem()
                item.setData(0,tLayer.layer())
                item.setData(1,feature)
                tbl.setItem(row,0,item)

                item = QtGui.QLabel(tLayer.layer().name())
                item.setToolTip("Double click to see feature")
                item.setStyleSheet("padding: 4px")
                tbl.setCellWidget(row,1,item)

                item = QtGui.QLabel(feature['name'])
                item.setToolTip("Double click to see feature")
                item.setStyleSheet("padding: 4px")
                tbl.setCellWidget(row,2,item)
  
                item = QtGui.QLabel(_topicManager.formatPayload(tLayer.topicType(),feature['payload']))
                item.setToolTip("Double click to see feature")
                item.setStyleSheet("padding: 4px")
                tbl.setCellWidget(row,3,item)

                row = row + 1

        tbl.setColumnHidden(0,True)
        tbl.resizeColumnsToContents()   
        tbl.horizontalHeader().setStretchLastSection(True)
        
    

    def _loadTopicManager(self,topicManagerId = 'digisense'):
        try:
            if self._create:
                self._broker.setTopicManager(topicManagerId)
            self._topicManager = topicManagerFactory.getTopicManager(self._broker,self._create)
            QObject.connect(self._topicManager,SIGNAL("topicManagerReady"),self._topicManagerLoaded)
            QObject.connect(self._topicManager,SIGNAL("topicManagerError"),self._topicManagerLoaded)
            self.Tabs.setTabEnabled(tlBrokerConfig.kTopicManagerTabId,False)
            widget = self._topicManager.getWidget()
            self.Tabs.addTab(widget,"Topics")
            self.dockWidget.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
            return True

        except Exception as e:
            Log.debug(e)
            
        
    def _topicManagerLoaded(self,state,obj):
        if state:
            self.Tabs.setTabEnabled(tlBrokerConfig.kTopicManagerTabId,True)
            self.connectApply.setEnabled(True)
        else:
            Log.critical(obj)


    def getTopicManager(self):
        return self.connectTopicManager.itemData( self.connectTopicManager.currentIndex())

    def setTopicManager(self,tmid):
        tmidx = self.connectTopicManager.findData(tmid)
        if tmidx > 0:
            self.connectTopicManager.setCurrentIndex(tmidx)
        else:
            self.connectTopicManager.setCurrentIndex(0)
            

   
    def getTopics(self):
        if self._topicManager == None:
            return []
        return self._topicManager.getTopics()
            
   
    def getBroker(self):
            
        self._broker.setName(self.getName())
        self._broker.setHost(self.getHost())
        self._broker.setPort(self.getPort())
        self._broker.setPoll(self.getPoll())
        self._broker.setKeepAlive(self.getKeepAlive())
        self._broker.setTopics(self.getTopics())
        self._broker.setTopicManager(self.getTopicManager())
        return self._broker

    def getName(self):
        return self.connectName.text()
   
    def setName(self,name):
        self.connectName.setText(name)

    def getHost(self):
        return self.connectHost.text()

    def setHost(self,host):
        self.connectHost.setText(host)

    def getPort(self):
        if len(self.connectPort.text()) > 0:
           return int(self.connectPort.text())
        return None

    def setPort(self,port):
        self.connectPort.setText(str(port))

    def getKeepAlive(self,default = "0"):
        val = self.connectKeepAlive.itemText(self.connectKeepAlive.currentIndex())
        if val == None or not val.isdigit():
            val = default
        return int(val)

    def setKeepAlive(self,keepalive):
        idx = self.connectKeepAlive.findText(str(keepalive))
        if idx == None:
            idx = 0
        self.connectKeepAlive.setCurrentIndex(idx)

    def getPoll(self):
        return int(self.connectPoll.itemText(self.connectPoll.currentIndex())) * 1000

    def setPoll(self,interval):
        _interval = int(float(1.0/1000) * float(interval))
        self.connectPoll.setCurrentIndex(self.connectPoll.findText(str(_interval)))

    def getTested(self):
        return self._tested

    def setTested(self,state = True):
        self._tested = state
        if state and self._topicManager == None:
            if self._loadTopicManager(self.getTopicManager()):
                self.connectTopicManager.setEnabled(False)
        else:
            pass
            #self.Tabs.setTabEnabled(1,False)

            
        
    def validate(self):
        if len(self.getName()) == 0:
            Log.alert("Please supply a name for this broker")
            return False
    
        if self.getTopicManager() == None:
            Log.alert("Please specify a Broker Type (Topic Manager)")
            return False
        
        if not Brokers.instance().uniqName(self._broker.id(),self.getName()):
            Log.alert("A broker named " + self.getName() + " already exists")
            return False

        if len(self.getHost()) == 0:
            Log.alert("Please supply a hostname")
            return False

        if self.getPort() == None:
            Log.alert("Please specify a port")
            return False
        
        return True
        
    
    def _test(self):
        if not self.validate():
            return
        testClient = tlMqttTest(self,self.getHost(),self.getPort())
        self.connectTest.setEnabled(False)

        QObject.connect(testClient, QtCore.SIGNAL("mqttOnConnect"), self._connectSuccess)
        QObject.connect(testClient, QtCore.SIGNAL("mqttConnectionError"), self._connectError)
        QObject.connect(testClient, QtCore.SIGNAL("mqttOnTimeout"), self._connectError)

        Log.progressPush("Testing Connection")
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));

        testClient.run()

    def _connectError(self,mqtt,msg = ""):
        self.connectTest.setEnabled(True)
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor));
        QObject.disconnect(mqtt, QtCore.SIGNAL("mqttOnConnect"), self._connectSuccess)
        QObject.disconnect(mqtt, QtCore.SIGNAL("mqttConnectionError"), self._connectError)
        Log.progressPop("Testing Connection")
        Log.progress(msg)
        Log.debug(msg)
        mqtt.kill()
        if self.getTested():
            self.setTested(False)

    def _connectSuccess(self,mqtt,obj, rc):
        self.connectTest.setEnabled(True)
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor));
        QObject.disconnect(mqtt, QtCore.SIGNAL("mqttOnConnect"), self._connectSuccess)
        QObject.disconnect(mqtt, QtCore.SIGNAL("mqttConnectionError"), self._connectError)
        Log.progressPop("Testing Connection")
        Log.progress("Connection successful!")
        mqtt.kill()
        self.setTested(True)

    def _help(self):
       webbrowser.open(Settings.getMeta('helpURL'))

    def _showLog(self,state):
        logDock = self._iface.mainWindow().findChild(QtGui.QDockWidget, 'MessageLog')
        if state:
            logDock.show()
        else:
            logDock.hide()


    def accept(self):
        print("accept")
        self.connectHelp.clicked.disconnect(self._help)
        self.connectTest.clicked.disconnect(self._test)
        super(tlBrokerConfig,self).accept()
        

    
