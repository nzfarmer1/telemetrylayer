# -*- coding: utf-8 -*-
"""
Layer Manager - managers groups, legends, and controls individual layers
"""
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSlot,SIGNAL
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from tlayer import tLayer as TLayer
from tlbrokers import tlBrokers as Brokers,BrokerNotFound
from tltopicmanagerfactory import tlTopicManagerFactory as TopicManagerFactory
from telemetrylayer import TelemetryLayer as telemetryLayer
from tlayerconfig import tLayerConfig as layerConfig
import os.path

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

from qgis.utils import qgsfunction
from qgis.core import QGis

_this = None

#def featureDialog(dialog,layerid,featureid):
#    Log.debug("Layer Manager " + str(_this))
    

class layerManager(QObject):

    _this = None
    _rebuildingLegend = False
    
    kBrokerId = "brokerId"
    
    @staticmethod
    def getLayers():
        layers = [] 
        for l in QgsMapLayerRegistry.instance().mapLayers().values():
            if TLayer.isTLayer(l):
                layers.append(l)
                
        return layers
    


    @staticmethod    
    def refresh():    
        for layer in tl.getLayers():
            layer.triggerRepaint()
            
    @staticmethod
    def instance():
        if layerManager._this == None:
            raise Exception('Telemetry Layer Manager not created')
        return layerManager._this

    def __init__(self,creator):
        Log.debug('init Layer Manager')
        super(layerManager,self).__init__()
        self._creator = creator
        self._iface =  creator.iface
        self._plugin_dir =  creator.plugin_dir
        self.disableDialog = False
        self.actions ={}
        self.menuName = Settings.getMeta('name')
        self._tLayers = {}
        layerManager._rebuildingLegend = False

        layers = layerManager.getLayers()
        if len(layers) > 0: # Existing layers
            for layer in layers:
                if self.initLayer(layer) == None:
                    self.removeLayer(layer,True)

        self._disable_enter_attribute_values_dialog_global_default =  QSettings().value( "/qgis/digitizing/disable_enter_attribute_values_dialog")
 
        self.actions['config'] = QAction(QIcon(":/plugins/digisense/icon.png"), u"Configure", self._iface.legendInterface() )

        self.actions['pause'] = QAction(
            QIcon(":/plugins/digisense/icon.png"),
            "Pause", self._iface.legendInterface())

        self.actions['resume'] = QAction(
            QIcon(":/plugins/digisense/icon.png"),
            "Resume", self._iface.legendInterface())

        self._iface.legendInterface().addLegendLayerAction(self.actions['resume']  ,self.menuName, u"id1", QgsMapLayer.VectorLayer, False )
        self._iface.legendInterface().addLegendLayerAction(self.actions['config']  , self.menuName, u"id1", QgsMapLayer.VectorLayer, False )
        self._iface.legendInterface().addLegendLayerAction(self.actions['pause']  , self.menuName, u"id1", QgsMapLayer.VectorLayer, False )

        #self.actions['resume'].setEnabled(False)
    
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layerWillBeRemoved) # change to when layer is loaded also!
       
        self._iface.legendInterface().currentLayerChanged.connect(self.currentLayerChanged) # change to when layer is loaded also!
        self._iface.mapCanvas().renderStarting.connect(self.renderStarting)

        QgsProject.instance().readProject.connect(self.readProject)
     
        QgsProject.instance().layerLoaded.connect(self.layerLoaded)
        
        mw = self._iface.mainWindow()
        self.lgd = mw.findChild(QTreeView, "theLayerTreeView")
        self.lgd.clicked.connect(self.legendPressed)
        self.lgd.doubleClicked.connect(self.legendDblClicked)
        self._iface.legendInterface().groupRelationsChanged.connect(self.legendRelationsChanged)
        
        TopicManagerFactory.registerAll()

        for layer in layers:
            layer.triggerRepaint()
        
        layerManager._this = self

    def _isBrokerGroup(self,nodeGrp):
        if 'Group' in str(type(nodeGrp)) and nodeGrp.customProperty(layerManager.kBrokerId,-1) != -1:
            return True
        else:
            return None

    def _getGroup(self,broker,create = False):
        root = QgsProject.instance().layerTreeRoot()
        # replace with _getGroupNode
        nodeGrp = root.findGroup(broker.name())
        if nodeGrp == None and create:
            nodeGrp = root.insertGroup(0,broker.name())
            nodeGrp.setCustomProperty(layerManager.kBrokerId,broker.id())

        return nodeGrp
        


    """
    Add new Layer to a Group. Create group if required
    """
 
    def _addLayerToGroup(self,layer,broker):

        li = self._iface.legendInterface()
        nodeGrp = self._getGroup(broker,True)
        nodeLayer = nodeGrp.findLayer(layer.id())
        if not nodeLayer:
             Log.debug("Moving node to group " + broker.name())
             root = QgsProject.instance().layerTreeRoot()
             nodeLayer = root.findLayer(layer.id())
             if nodeLayer == None:
                return None
             newNodeLayer = nodeLayer.clone()
             nodeGrp.insertChildNode(1,newNodeLayer)
             nodeGrp.setCustomProperty(layerManager.kBrokerId,broker.id())
             nodeLayer.parent().removeChildNode(nodeLayer)
             nodeLayer =  newNodeLayer

        return nodeLayer
             
    def readProject(self):
        Log.debug("readProject")
        return

    """
    If the list of brokers have changed checked the integrity
    """

    def rebuildLegend(self):
        if  layerManager._rebuildingLegend:
            return

        Log.debug("rebuildLegend " + str(layerManager._rebuildingLegend))
        layerManager._rebuildingLegend = True
        
        root = QgsProject.instance().layerTreeRoot()
        try:
            parentsToRoot = []
            for lid,tLayer in self.getTLayers(False).iteritems():
                if Brokers.instance().find(TLayer.getBrokerId(tLayer.layer())) == None:
                    continue

                broker = tLayer.getBroker()
                nodeLayer  = self._addLayerToGroup(tLayer.layer(),broker)
                if nodeLayer.parent().parent() != root:
                    if not nodeLayer.parent() in parentsToRoot:
                        parentsToRoot.append(nodeLayer.parent())
           
            # handle nested node groups!
            for parent in parentsToRoot:
                    broker = Brokers.instance().findByName(parent.name())
                    nodeGroup = root.addGroup(broker.name())
                    nodeGroup.setCustomProperty(layerManager.kBrokerId,broker.id())
                    for child in parent.findLayers():
                       nodeGroup.insertChildNode(1,child.clone())
                    parent.removeAllChildren()                   
                    parent.parent().removeChildNode(parent)
                    
            #handle removed brokers
            removed = []
            for lid in root.findLayerIds():
                layer = QgsMapLayerRegistry.instance().mapLayer(lid)
                if TLayer.isTLayer(layer):
                    bid = TLayer.getBrokerId(layer)
                    if Brokers.instance().find(bid) == None:
                        Log.debug("Broker not found")
                        nodeLayer = root.findLayer(lid)
                        if not nodeLayer.parent().name() in removed:
                            removed.append(nodeLayer.parent().name())
                        root.removeChildNode(nodeLayer)
            
            # Remove empty or groups referencing older renamed brokers
            for node in root.children():
                if self._isBrokerGroup(node) and len(node.children()) == 0:
                       removed.append(node.name())
                    
            # perform removal                
            for group in removed:
                Log.warn("Broker " + group + " not found in list of Brokers. Removing from legend" )
                nodeGrp = root.findGroup(group)
                root.removeChildNode(root.findGroup(group))
                    
        except Exception as e:
            Log.debug(e)
            
        layerManager._rebuildingLegend = False
 
    def getTLayers(self,add = True):  
        for l in layerManager.getLayers():
                self.getTLayer(l.id(),add)

        return self._tLayers
        
    def legendPressed(self,item):
        pass
            
    def legendDblClicked(self,item):

        model   = 	QgsLayerTreeModel( QgsProject.instance().layerTreeRoot())
        node    =   model.index2node(item)
        if self._isBrokerGroup(node):
            bid = node.customProperty(layerManager.kBrokerId,-1)
            broker = Brokers.instance().find(bid)
            if broker !=None:
                telemetryLayer.instance().show(broker)
            else:
                # handle missing broker
                pass

    
    def legendRelationsChanged(self):
        """
        Note: when a projec is loading this will cause
        multiple calls to rebuildLegend
        and the possibility of multiple broker removals
        """
        self.rebuildLegend()
        
    def brokersLoaded(self,changed = []):
        remove = []
        Log.debug("Brokers Loaded")
        for lid,tLayer in self.getTLayers().iteritems():
            old_broker = tLayer.getBroker()
            broker = Brokers.instance().find(old_broker.id())
            if broker == None:
                remove.append(tLayer.layer())
                continue
            tLayer.setBroker(broker)
        
        if len(remove) >0:
            Log.alert("Broker Not found - Removing associated layers!")
            for layer in remove:
                self.removeLayer(tLayer.layer(),False)

        self.rebuildLegend()
        for lid,tLayer in self.getTLayers().iteritems():
            if tLayer.isRunning() and tLayer.getBroker().id() in changed:
                Log.debug("Restarting  " + tLayer.getBroker().name() )
                tLayer.restart()
        
    def layerPropertiesChanged(self,val = 0):
        Log.debug("Layer Properties Changed " + str(val))
    
    def renderStarting(self):
        for lid,tLayer in self.getTLayers().iteritems():
                visible = self._iface.legendInterface().isLayerVisible(tLayer.layer())
                    
               #if not visible:
                #    self.actions['pause' + lid].setEnabled(False)
                #    self.actions['resume' + lid].setEnabled(False)
                #else:
                #    self.actions['pause' + lid].setEnabled(not tLayer.isPaused())
                #    self.actions['resume' + lid].setEnabled(tLayer.isPaused())
                tLayer.refresh(visible and not tLayer.isPaused())
        

    def getTLayer(self,lid,add = True):
        remove = []    
        if  lid in self._tLayers:
            return self._tLayers[lid]
        elif add == True:
            try:
                layer = QgsMapLayerRegistry.instance().mapLayer(lid)
                self._tLayers[lid] = TLayer(self,QgsMapLayerRegistry.instance().mapLayer(lid))
                layer.triggerRepaint()
                return self._tLayers[lid]
            except BrokerNotFound:
                   
                   return None
            except Exception as e:
                Log.warn(e.__str__())
        else:
            return None

    def delTLayer(self,lid):
        try:
            del self._tLayers[lid]
        except:
            pass

    def initLayer(self,layer,broker=None,topicType=None):
        
        tLayer = None
        if broker != None and topicType !=None:
        
            QgsMapLayerRegistry.instance().addMapLayer(layer)  # API >= 1.9
            lid = layer.id()
            
            tLayer  = TLayer(self,
                                QgsMapLayerRegistry.instance().mapLayer(lid),
                                broker,
                                topicType)
            
            if tLayer == None:
                Log.debug("Unable to create Telemetry Layer")
                return None
            else:
                self._tLayers[lid] = tLayer
        else:
            tLayer = self.getTLayer(layer.id(),True)
            if tLayer == None:
                return None

        self.actions['config' + layer.id()] = QAction(
            QIcon(":/plugins/digisense/icon.png"),
            u"Configure", self._iface.legendInterface() )

        self.actions['pause' + layer.id()] = QAction(
            QIcon(":/plugins/digisense/icon.png"),
            u"Pause", self._iface.legendInterface())

        self.actions['resume' + layer.id()] = QAction(
            QIcon(":/plugins/digisense/icon.png"),
            u"Resume", self._iface.legendInterface())

        if 0: # disable menu actions
            self._iface.legendInterface().addLegendLayerAction(self.actions['config' + layer.id()] , self.menuName, u"id2", QgsMapLayer.VectorLayer, False )
            self._iface.legendInterface().addLegendLayerAction(self.actions['pause' + layer.id()]  , self.menuName, u"id2", QgsMapLayer.VectorLayer, False )
            self._iface.legendInterface().addLegendLayerAction(self.actions['resume' + layer.id()] , self.menuName, u"id2", QgsMapLayer.VectorLayer, False )
     
            self._iface.legendInterface().addLegendLayerActionForLayer(  self.actions['config' + layer.id()], layer )
            self._iface.legendInterface().addLegendLayerActionForLayer(  self.actions['pause'  + layer.id()], layer )
            self._iface.legendInterface().addLegendLayerActionForLayer(  self.actions['resume' + layer.id()], layer )
    
            QObject.connect(self.actions['config' + layer.id()], SIGNAL("triggered()"),lambda: self.editLayer(layer.id()))
            QObject.connect(self.actions['pause'  + layer.id()], SIGNAL("triggered()"),lambda: self.pauseLayer(layer.id()))
            QObject.connect(self.actions['resume' + layer.id()], SIGNAL("triggered()"),lambda: self.resumeLayer(layer.id()))
            self.actions['pause' + layer.id()].setEnabled(False)
        
#        layer.beforeRollBack.connect(self.beforeRollBack) #implement
        layer.featureAdded.connect(self.featureAdded) #implement
        layer.featureDeleted.connect(self.featureDeleted) #implement
        
#        layer.repaintRequested.connect(tLayer.repaintRequested) # Refresh method was better

        layer.editingStarted.connect(tLayer.layerEditStarted) # change to when layer is loaded also!
        layer.editingStopped.connect(tLayer.layerEditStopped)
        QApplication.instance().focusChanged.connect(tLayer.focusChange)
        
        layer.triggerRepaint()
        return self.getTLayer(layer.id(),False)
    
    def removeLayer(self,layer,confirm = True):
        lid = layer.id()
        if confirm and Log.confirm("Are you sure you want to remove layer " + layer.name() + "?"):
            try:
                Log.debug("Removing layer")
 #               QgsMapLayerRegistry.instance().removeMapLayers(layer.id())
                QgsProject.instance().layerTreeRoot().removeLayer(layer)

                self.delTLayer(lid)
            except Exception as e:
                Log.debug("Layer removed " + str(e))
        elif not confirm:
            QgsProject.instance().layerTreeRoot().removeLayer(layer)
        
#         QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
            self.delTLayer(lid)

        Log.debug("Layer removed")
 
        
    def layerWillBeRemoved(self,layerId):
        layer = QgsMapLayerRegistry.instance().mapLayer(layerId)
        try:
            self._iface.legendInterface().setLayerVisible(layer,False)
            tLayer =  self.getTLayer(layerId)
            
            if tLayer !=None:
                tLayer.tearDown()
                self.delTLayer(layerId)
                self.rebuildLegend()

        except Exception as e:
            self.delTLayer(layerId)
            Log.debug(e)

    def pauseLayer(self,lid):
        tLayer = self.getTLayer(lid)
        tLayer.setPaused(True)
        #self.actions['pause'+lid].setEnabled(False)
        #self.actions['resume'+lid].setEnabled(True)
        tLayer.layer().triggerRepaint()

    def resumeLayer(self,lid):
        tLayer = self.getTLayer(lid)
        tLayer.setPaused(False)
        #self.actions['pause'+lid].setEnabled(True)
        #self.actions['resume'+lid].setEnabled(False)
        tLayer.layer().triggerRepaint()

    def editLayer(self,lid):
        tLayer = self.getTLayer(lid)
        
        dlg = tLayer.getConfigDialog()
        if not dlg.dockWidget.isVisible():
            self._creator.iface.addDockWidget( Qt.LeftDockWidgetArea,  dlg.dockWidget )
            dlg.connectApply.clicked.connect(lambda : tLayer.update(dlg))
        
    def layerLoaded(self,i,n):
        if i == n: # Last layer
            for layer in self.getLayers():
                    self.initLayer(layer)
    
    def getIface(self):
        return self._iface
    

    def createEmptyLayer(self):
        dlg = layerConfig(self)
        result = dlg.exec_()
        if (result == 0): # object will be garbage collected
            return False

        geomType    = 'Point' + '?crs=proj4:' + QgsProject.instance().readEntry("SpatialRefSys","/ProjectCRSProj4String")[0] #dodana linia - from Menory Layer Module
        broker      = dlg.getBroker()
        topicType   = dlg.getTopicType()
        layer       = QgsVectorLayer(geomType,topicType, 'memory') #zmieniona linia
        
        tLayer = self.initLayer(layer,broker,topicType)
        #self._iface.legendInterface().setCurrentLayer(layer)
        Log.debug("telemetrylayermanager - set Current Layer")
        
        self.rebuildLegend()
        layer.triggerRepaint()
 

    def beforeRollBack(self):
        layer    = self._iface.activeLayer()
        tLayer   = self.getTLayer(layer.id())
        tLayer.beforeRollBack()

    def featureAdded(self,fid):
        layer = self._iface.activeLayer()
        if layer == None:
            return
        tLayer = self.getTLayer(layer.id())
        if tLayer == None:
            Log.debug("Error Loading tLayer")
            return
        result = tLayer.addFeature(fid)
        Log.debug("Adding Feature")
        if result !=None:
                tLayer.restart()


    def featureDeleted(self,fid):
        if fid <0:
            return
        layer = self._iface.activeLayer()
        tLayer = self.getTLayer(layer.id())
        Log.debug("Feature Deleted " + str(fid))
        tLayer.restart()

        
    def currentLayerChanged(self):
        layer = self._iface.activeLayer()
        # Ensure settings dialog doesn't come up
        
        if TLayer.isTLayer(layer):
             QSettings().setValue( '/qgis/digitizing/disable_enter_attribute_values_dialog', True )
        else:
             QSettings().setValue( '/qgis/digitizing/disable_enter_attribute_values_dialog', 
                                  self._disable_enter_attribute_values_dialog_global_default)



    def tearDownTLayers(self):

        for lid,tLayer in self.getTLayers(False).iteritems():
           QApplication.instance().focusChanged.disconnect(tLayer.focusChange)
 #          if 0:
 #           self._iface.legendInterface().removeLegendLayerAction( self.actions['config'+lid] )
 #           self._iface.legendInterface().removeLegendLayerAction(  self.actions['pause'+lid] )
 #           self._iface.legendInterface().removeLegendLayerAction(  self.actions['resume'+lid] )
           #tLayer.layer().beforeRollBack.disconnect(self.beforeRollBack) #implement
           tLayer.layer().featureAdded.disconnect(self.featureAdded) #implement
           tLayer.layer().featureDeleted.disconnect(self.featureDeleted) #implement
           
#           tLayer.layer().repaintRequested.disconnect(tLayer.repaintRequested) 
           tLayer.layer().editingStarted.disconnect(tLayer.layerEditStarted) # change to when layer is loaded also!
           tLayer.layer().editingStopped.disconnect(tLayer.layerEditStopped)
           tLayer.tearDown()

    def tearDown(self):
        Log.debug("Layer Manager Teardown")
        self.tearDownTLayers()
        self._iface.legendInterface().groupRelationsChanged.disconnect(self.legendRelationsChanged)
        if 0:
            self._iface.legendInterface().removeLegendLayerAction( self.actions['config'] )
            self._iface.legendInterface().removeLegendLayerAction(  self.actions['pause'] )
            self._iface.legendInterface().removeLegendLayerAction(  self.actions['resume'] )
        QgsProject.instance().readProject.disconnect(self.readProject)
        QgsProject.instance().layerLoaded.disconnect(self.layerLoaded)
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layerWillBeRemoved)
        self.lgd.clicked.disconnect(self.legendPressed)
        self.lgd.doubleClicked.disconnect(self.legendDblClicked)

        self._iface.legendInterface().currentLayerChanged.disconnect(self.currentLayerChanged) # change to when layer is loaded also!
        self._iface.mapCanvas().renderStarting.disconnect(self.renderStarting)

        TopicManagerFactory.unregisterAll()
    
    def __del__(self):
        pass


