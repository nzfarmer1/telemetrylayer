# -*- coding: utf-8 -*-
"""
Layer Manager - managers groups, legends, and controls individual layers

"""
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSlot, SIGNAL
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from tlayer import tLayer as TLayer
from tlbrokers import tlBrokers as Brokers, BrokerNotFound, BrokerNotSynced, BrokersNotDefined
from tltopicmanagerfactory import tlTopicManagerFactory as TopicManagerFactory
from telemetrylayer import TelemetryLayer as telemetryLayer
from tlayerconfig import tLayerConfig as layerConfig
from tlfeaturedock import tlFeatureDock as FeatureDock
import os.path,sys,traceback,json

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

from qgis.core import QGis

_this = None


class layerManager(QObject):
    """
    Manage all individual "telemetry" layers
    - providing QObject signal connect to the iFace
    - managing the legend group interface/integrity
    - responding to request to add new layers, add/delete features
    
    Note: breaks the naming conventions. should be called tLayerManager perhaps?
    """

    _this = None
    _rebuildingLegend = False


    @staticmethod
    def getLayers():
        layers = []
        for l in QgsMapLayerRegistry.instance().mapLayers().values():
            if TLayer.isTLayer(l):
                layers.append(l)

        return layers


    @staticmethod
    def refresh():
        for layer in layerManager.getLayers():
            layer.triggerRepaint()

    @staticmethod
    def instance():
        if layerManager._this is None:
            raise Exception('Telemetry Layer Manager not created')
        return layerManager._this

    def showFeatureDock(self,layer,feature):
        try:
            key = (layer.id(),feature.id())
            if key in self._featureDocks:
                dock = self._featureDocks[key]
                if dock is not None:
                    if dock.isVisible():
                        return
                    else:
                        Log.debug(str(dock) + ' show') 
                        dock.show()
                        return
            
            self._featureDocks[key] = FeatureDock(self._iface,
                                            self.getTLayer(layer.id(),False),
                                            feature)
            pass
        except Exception as e:
            Log.debug('showFeatureDock: ' + str(e))

    def _showFeatureDocks(self):
        for (lid,fid) in self._featureDocks.keys():
            try:
                dock = self._featureDocks[(lid,fid)]
                if dock and dock.isVisible():
                    dock.close()
            except Exception as e:
                Log.debug("Error closing existing docks")
        self._featureDocks = {}
        
        reopen = json.loads(Settings.getp('featureDocks',json.dumps([])))
        for (layerId,featureId) in reopen:
            try:
                layer = QgsMapLayerRegistry.instance().mapLayer(layerId)
                request = QgsFeatureRequest(featureId)
                feature = next(layer.getFeatures(request), None)
                if layer and feature:       
                    self.showFeatureDock(layer,feature)
            except Exception as e:
                Log.debug("Error reloading feature dock " +str(e))

    def __init__(self, creator):
        Log.debug('init Layer Manager')
        super(layerManager, self).__init__()
        self._creator = creator
        self._iface = creator.iface
        self._plugin_dir = creator.plugin_dir
        self.disableDialog = False
        self.actions = {}
        self.menuName = Settings.getMeta('name')
        self._tLayers = {}
        self._featureDocks = {}
        layerManager._rebuildingLegend = False
        QgsProject.instance().readProject.connect(self._showFeatureDocks)
#        QgsProject.instance().writeProject.connect(self.tearDownDocks)
        QgsProject.instance().writeMapLayer.connect(self._writeMapLayer)

        layers = layerManager.getLayers()
        if len(layers) > 0:  # Existing layers
            for layer in layers:
                if self.initLayer(layer) is None:
                    self.removeLayer(layer, True)

        self._disable_enter_attribute_values_dialog_global_default = QSettings().value(
            "/qgis/digitizing/disable_enter_attribute_values_dialog")

        self.actions['config'] = QAction(QIcon(":/plugins/telemetrylayer/icon.png"), u"Configure",
                                         self._iface.legendInterface())

        self.actions['pause'] = QAction(
            QIcon(":/plugins/telemetrylayer/icon.png"),
            "Pause", self._iface.legendInterface())

        self.actions['resume'] = QAction(
            QIcon(":/plugins/telemetrylayer/icon.png"),
            "Resume", self._iface.legendInterface())

        self._iface.legendInterface().addLegendLayerAction(self.actions['resume'], self.menuName, u"id1",
                                                           QgsMapLayer.VectorLayer, False)
        self._iface.legendInterface().addLegendLayerAction(self.actions['config'], self.menuName, u"id1",
                                                           QgsMapLayer.VectorLayer, False)
        self._iface.legendInterface().addLegendLayerAction(self.actions['pause'], self.menuName, u"id1",
                                                           QgsMapLayer.VectorLayer, False)

        # self.actions['resume'].setEnabled(False)

        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(
            self.layerWillBeRemoved)  # change to when layer is loaded also!

        self._iface.legendInterface().currentLayerChanged.connect(
            self.currentLayerChanged)  # change to when layer is loaded also!
        self._iface.mapCanvas().renderStarting.connect(self.renderStarting)

        QgsProject.instance().readProject.connect(self.readProject)
        QgsProject.instance().readMapLayer.connect(self.readMapLayer)

        QgsProject.instance().layerLoaded.connect(self.layerLoaded)

        mw = self._iface.mainWindow()
        self.lgd = mw.findChild(QTreeView, "theLayerTreeView")
        self.lgd.clicked.connect(self.legendPressed)
        self.lgd.doubleClicked.connect(self.legendDblClicked)
        self._iface.legendInterface().groupRelationsChanged.connect(self.legendRelationsChanged)

        for layer in layers:
            layer.triggerRepaint()

        layerManager._this = self

    def _isBrokerGroup(self, nodeGrp):
        if 'Group' in str(type(nodeGrp)) and nodeGrp.customProperty(TLayer.kBrokerId, -1) != -1:
            return True
        else:
            return None

    def _getGroup(self, broker, create=False):
        root = QgsProject.instance().layerTreeRoot()
        # replace with _getGroupNode
        nodeGrp = root.findGroup(broker.name())
        if nodeGrp is None and create:
            
            nodeGrp = root.insertGroup(0, broker.name())
            # Changed from len(root.children()) to 0 to place at top of tree!
            # nodeGrp.setToolTip("Double click to view features")
            nodeGrp.setCustomProperty(TLayer.kBrokerId, broker.id())

        return nodeGrp


    """
    Add new Layer to a Group. Create group if required
    """

    def _addLayerToGroup(self, layer, broker):

        li = self._iface.legendInterface()
        nodeGrp = self._getGroup(broker, True)
        nodeLayer = nodeGrp.findLayer(layer.id())
        if not nodeLayer:
            Log.debug("Moving node to group " + broker.name())
            root = QgsProject.instance().layerTreeRoot()
            nodeLayer = root.findLayer(layer.id())
            self._iface.legendInterface().setCurrentLayer(layer)
            if nodeLayer is None:
                return None
            newNodeLayer = nodeLayer.clone()
            nodeGrp.insertChildNode(1, newNodeLayer)
            nodeGrp.setCustomProperty(TLayer.kBrokerId, broker.id())
            nodeLayer.parent().removeChildNode(nodeLayer)
            nodeLayer = newNodeLayer

        return nodeLayer

    def readProject(self):
        return
        for lid, tLayer in self.getTLayers().iteritems():
            Log.debug("Adding V2 Format data to loaded layers")
            # Change this to add in only the path details!
            tLayer._setFormatters(True)  # Memory Layer Saver doesn't save some V2 format data
           
        return
    
    def readMapLayer(self,layer,dom):
        pass
#        tLayer = self.getTLayer(layer.id(),False)
#        if tLayer is None:
#            Log.debug(str(layer.id()) + " not tLayer" )
#            Log.debug(str(layer.id()) + " => " + str(TLayer.isTLayer(layer)) )
#            return
#        if TLayer.isTLayer(layer):
#            tLayer = self.getTLayer(layer.id(),add)
           # tLayer._setFormatters(True)  # Memory Layer Saver doesn't save some V2 format data
           
    """
    If the list of brokers have changed checked the integrity
    """

    def rebuildLegend(self):
        
        if layerManager._rebuildingLegend:
            return

        layerManager._rebuildingLegend = True

        root = QgsProject.instance().layerTreeRoot()
        try:
            parentsToRoot = []
            for lid, tLayer in self.getTLayers(False).iteritems():
                if Brokers.instance().find(TLayer.getBrokerId(tLayer.layer())) is None:
                    continue

                broker = tLayer.getBroker()
                nodeLayer = self._addLayerToGroup(tLayer.layer(), broker)
                if not nodeLayer:
                    return
                if nodeLayer and nodeLayer.parent().parent() != root:
                    if not nodeLayer.parent() in parentsToRoot:
                        parentsToRoot.append(nodeLayer.parent())

            # handle nested node groups!
            for parent in parentsToRoot:
                broker = Brokers.instance().findByName(parent.name())
                nodeGroup = root.addGroup(broker.name())
                nodeGroup.setCustomProperty(TLayer.kBrokerId, broker.id())
                for child in parent.findLayers():
                    nodeGroup.insertChildNode(1, child.clone())
                parent.removeAllChildren()
                parent.parent().removeChildNode(parent)
                

            # handle removed brokers
            removed = []
            for lid in root.findLayerIds():
                layer = QgsMapLayerRegistry.instance().mapLayer(lid)
                if TLayer.isTLayer(layer):
                    bid = TLayer.getBrokerId(layer)
                    if Brokers.instance().find(bid) is None:
                        Log.debug("Broker not found")
                        nodeLayer = root.findLayer(lid)
                        if not nodeLayer.parent().name() in removed:
                            removed.append(nodeLayer.parent())
                        root.removeChildNode(nodeLayer)

            # Remove empty or groups referencing older renamed brokers
            for node in root.children():
                if self._isBrokerGroup(node) and not node.children():
                    removed.append(node)
             
            # perform removal                
            for node in removed:
                #Log.progress("Broker " + group + " not found in list of Brokers. Removing from legend")
                #nodeGrp     = root.findGroup(group)
                root.removeChildNode(node)
    
        except Exception as e:
            Log.debug(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.debug(repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback)))

        layerManager._rebuildingLegend = False

    def getTLayers(self, add=True):
        for l in layerManager.getLayers():
            self.getTLayer(l.id(), add)

        return self._tLayers

    def legendPressed(self, item):
        model = self.lgd
        item = "Broker4"

        # Items = model.match(model.index(0, 0),Qt.DisplayRole,
        #            QVariant.fromValue(item),
        #            2,
        #            Qt.MatchRecursive)
        #      Log.debug(Items)
        #        for child in self.lgd.children():
        #           Log.debug(item)
        #if 'QWidget' in str(type(child)):
        #   Log.debug(child.children())

        pass

    def legendDblClicked(self, item):

        model = QgsLayerTreeModel(QgsProject.instance().layerTreeRoot())
        node = model.index2node(item)
        if self._isBrokerGroup(node):
            bid = node.customProperty(TLayer.kBrokerId, -1)
            broker = Brokers.instance().find(bid)
            if broker is not None:
                telemetryLayer.instance().show(broker)
            else:
                # handle missing broker
                pass


    def legendRelationsChanged(self):
        """
        Note: when a project is loading this will cause
        multiple calls to rebuildLegend
        and the possibility of multiple broker removals
        """

        self.rebuildLegend()

    def brokersLoaded(self, changed=[]):
        remove = []
        for  tLayer in self.getTLayers().itervalues():
            old_broker = tLayer.getBroker()
            broker = Brokers.instance().find(old_broker.id())
            if broker is None:
                remove.append(tLayer.layer())
                continue
            tLayer.setBroker(broker)

        if len(remove) > 0:
            Log.alert("Broker Not found - Removing associated layers!")
            for layer in remove:
                tLayer.kill()
                self.removeLayer(tLayer.layer(), False)

        self.rebuildLegend()
        for lid, tLayer in self.getTLayers().iteritems():
            if tLayer.isRunning() and tLayer.getBroker().id() in changed:
                Log.debug("Restarting  " + tLayer.getBroker().name())
                tLayer.restart()


    def brokerInUse(self,bid):
        """ Return try if a layer exists with the broker id """
        found = False
        for  tLayer in self.getTLayers().itervalues():
             found = found or (bid == tLayer.getBroker().id())
        return found

    def layerPropertiesChanged(self, val=0):
        Log.debug("Layer Properties Changed " + str(val))

    def renderStarting(self):
        for tLayer in self.getTLayers().itervalues():
            visible = self._iface.legendInterface().isLayerVisible(tLayer.layer())
            # if not visible:
            #    self.actions['pause' + lid].setEnabled(False)
            #    self.actions['resume' + lid].setEnabled(False)
            #else:
            #    self.actions['pause' + lid].setEnabled(not tLayer.isPaused())
            #    self.actions['resume' + lid].setEnabled(tLayer.isPaused())
            tLayer.refresh(visible and not tLayer.isPaused())


    def getTLayer(self, lid, add=True):
        remove = []
        if lid in self._tLayers:
            return self._tLayers[lid]
        elif add:
            try:
                layer = QgsMapLayerRegistry.instance().mapLayer(lid)
                self._tLayers[lid] = TLayer(self, QgsMapLayerRegistry.instance().mapLayer(lid))
                layer.triggerRepaint()
                return self._tLayers[lid]
            except BrokerNotFound:

                return None
            except Exception as e:
                Log.warn(e.__str__())
        else:
            return None

    def delTLayer(self, lid):
        try:
            del self._tLayers[lid]
        except:
            pass

    def initLayer(self, layer, broker=None, topicType=None):

        tLayer = None
        if broker is not None and topicType is not None:

            QgsMapLayerRegistry.instance().addMapLayer(layer)  # API >= 1.9
            lid = layer.id()

            tLayer = TLayer(self,
                            QgsMapLayerRegistry.instance().mapLayer(lid),
                            broker,
                            topicType)

            if tLayer is None:
                Log.debug("Unable to create Telemetry Layer")
                return None
            else:
                self._tLayers[lid] = tLayer
        else:
            tLayer = self.getTLayer(layer.id(), True)
            if tLayer is None:
                return None

        self.actions['config' + layer.id()] = QAction(
            QIcon(":/plugins/telemetrylayer/icon.png"),
            u"Configure", self._iface.legendInterface())

        self.actions['pause' + layer.id()] = QAction(
            QIcon(":/plugins/telemetrylayer/icon.png"),
            u"Pause", self._iface.legendInterface())

        self.actions['resume' + layer.id()] = QAction(
            QIcon(":/plugins/telemetrylayer/icon.png"),
            u"Resume", self._iface.legendInterface())

        if 0:  # disable menu actions
            self._iface.legendInterface().addLegendLayerAction(self.actions['config' + layer.id()], self.menuName,
                                                               u"id2", QgsMapLayer.VectorLayer, False)
            self._iface.legendInterface().addLegendLayerAction(self.actions['pause' + layer.id()], self.menuName,
                                                               u"id2", QgsMapLayer.VectorLayer, False)
            self._iface.legendInterface().addLegendLayerAction(self.actions['resume' + layer.id()], self.menuName,
                                                               u"id2", QgsMapLayer.VectorLayer, False)

            self._iface.legendInterface().addLegendLayerActionForLayer(self.actions['config' + layer.id()], layer)
            self._iface.legendInterface().addLegendLayerActionForLayer(self.actions['pause' + layer.id()], layer)
            self._iface.legendInterface().addLegendLayerActionForLayer(self.actions['resume' + layer.id()], layer)

            QObject.connect(self.actions['config' + layer.id()], SIGNAL("triggered()"),
                            lambda: self.editLayer(layer.id()))
            QObject.connect(self.actions['pause' + layer.id()], SIGNAL("triggered()"),
                            lambda: self.pauseLayer(layer.id()))
            QObject.connect(self.actions['resume' + layer.id()], SIGNAL("triggered()"),
                            lambda: self.resumeLayer(layer.id()))
            self.actions['pause' + layer.id()].setEnabled(False)

        # layer.beforeRollBack.connect(self.beforeRollBack) #implement
        layer.featureAdded.connect(self.featureAdded)  # implement
        layer.featureDeleted.connect(self.featureDeleted)  # implement

        # layer.repaintRequested.connect(tLayer.repaintRequested) # Refresh method was better

        layer.editingStarted.connect(tLayer.layerEditStarted)  # change to when layer is loaded also!
        layer.editingStopped.connect(tLayer.layerEditStopped)
        QApplication.instance().focusChanged.connect(tLayer.focusChange)

        layer.triggerRepaint()
        return self.getTLayer(layer.id(), False)

    def removeLayer(self, layer, confirm=True):
        lid = layer.id()
        if confirm and Log.confirm("Are you sure you want to remove layer " + layer.name() + "?"):
            try:
                Log.debug("Removing layer")
                # QgsMapLayerRegistry.instance().removeMapLayers(layer.id())
                QgsProject.instance().layerTreeRoot().removeLayer(layer)

                self.delTLayer(lid)
            except Exception as e:
                Log.debug("Layer removed " + str(e))
        elif not confirm:
            QgsProject.instance().layerTreeRoot().removeLayer(layer)

            # QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
            self.delTLayer(lid)

        Log.debug("Layer removed")


    def layerWillBeRemoved(self, layerId):
        layer = QgsMapLayerRegistry.instance().mapLayer(layerId)
        try:
            self._iface.legendInterface().setLayerVisible(layer, False)
            tLayer = self.getTLayer(layerId)

            if tLayer is not None:
                self.tearDownDocks(layerId)
                tLayer.tearDown()
                self.delTLayer(layerId)
                self.rebuildLegend()

        except Exception as e:
            self.delTLayer(layerId)
            Log.debug(e)

    def pauseLayer(self, lid):
        tLayer = self.getTLayer(lid)
        tLayer.setPaused(True)
        # self.actions['pause'+lid].setEnabled(False)
        #self.actions['resume'+lid].setEnabled(True)
        tLayer.layer().triggerRepaint()

    def resumeLayer(self, lid):
        tLayer = self.getTLayer(lid)
        tLayer.setPaused(False)
        # self.actions['pause'+lid].setEnabled(True)
        #self.actions['resume'+lid].setEnabled(False)
        tLayer.layer().triggerRepaint()

    def editLayer(self, lid):
        tLayer = self.getTLayer(lid)

        dlg = tLayer.getConfigDialog()
        if not dlg.dockWidget.isVisible():
            self._creator.iface.addDockWidget(Qt.LeftDockWidgetArea, dlg.dockWidget)
            dlg.connectApply.clicked.connect(lambda: tLayer.update(dlg))

    def layerLoaded(self, i, n):
        if i == n:  # Last layer
            for layer in self.getLayers():
                if self.getTLayer(layer.id(),False) is None:
                    self.initLayer(layer)

    def getIface(self):
        return self._iface


    def createEmptyLayer(self):
        try:
            telemetryLayer.instance().checkBrokerConfig()
        except BrokerNotSynced:
            Log.progress("Please save any broker configurations first")
        except BrokersNotDefined:
            Log.progress("Please configure your MQTT Brokers first - see Plugin -> Telemetry Layer -> Configure")
            return

        dlg = layerConfig(self)
        result = dlg.exec_()
        if result == 0:  # object will be garbage collected
            return False

        geomType = 'Point' + '?crs=proj4:' + QgsProject.instance().readEntry("SpatialRefSys", "/ProjectCRSProj4String")[
            0]  # dodana linia - from Menory Layer Module
        broker = dlg.getBroker()
        topicType = dlg.getTopicType()
        layer = QgsVectorLayer(geomType, topicType, 'memory')  # zmieniona linia

        tLayer = self.initLayer(layer, broker, topicType)
        # self._iface.legendInterface().setCurrentLayer(layer)
        Log.debug("telemetrylayermanager - set Current Layer")

        self.rebuildLegend()
        layer.triggerRepaint()


    def beforeRollBack(self):
        layer = self._iface.activeLayer()
        tLayer = self.getTLayer(layer.id())
        tLayer.beforeRollBack()

    def featureAdded(self, fid):
#        Log.debug("feature Added" + str(fid))
        request = QgsFeatureRequest(fid)
        layer = self._iface.activeLayer()
        feature = next(layer.getFeatures(request), None)
        try:
            featureExists = feature and feature['topic']
        except IndexError:
            featureExists = False
        
        #if fid < 0 and "Feature Attributes" in QgsApplication.activeWindow().windowTitle():
         #   return
        
        #if fid >0:
         #   return
         
        layer = self._iface.activeLayer()
        if layer is None:
            return
        tLayer = self.getTLayer(layer.id())

        if featureExists:
            tLayer.applyFeature(feature)
            return
        
        if tLayer is None:
            Log.debug("Error Loading tLayer")
            return
        result = tLayer.addFeature(fid)
        Log.debug("Adding Feature")
        if result is not None:
            tLayer.restart()


    def featureDeleted(self, fid):
        if fid < 0:
            return
        Log.debug(str(fid) + " Deleted")
        layer = self._iface.activeLayer()
        if layer is None:
            return
        tLayer = self.getTLayer(layer.id())
        Log.debug("Feature Deleted " + str(fid))
        tLayer.restart()


    def currentLayerChanged(self):
        layer = self._iface.activeLayer()
        # Ensure settings dialog doesn't come up

        if TLayer.isTLayer(layer):
            QSettings().setValue('/qgis/digitizing/disable_enter_attribute_values_dialog', True)
        else:
            QSettings().setValue('/qgis/digitizing/disable_enter_attribute_values_dialog',
                                 self._disable_enter_attribute_values_dialog_global_default)


    def tearDownTLayers(self):

        for lid, tLayer in self.getTLayers(False).iteritems():
            QApplication.instance().focusChanged.disconnect(tLayer.focusChange)
            # if 0:
            #           self._iface.legendInterface().removeLegendLayerAction( self.actions['config'+lid] )
            #           self._iface.legendInterface().removeLegendLayerAction(  self.actions['pause'+lid] )
            #           self._iface.legendInterface().removeLegendLayerAction(  self.actions['resume'+lid] )
            #tLayer.layer().beforeRollBack.disconnect(self.beforeRollBack) #implement
            tLayer.layer().featureAdded.disconnect(self.featureAdded)  #implement
            tLayer.layer().featureDeleted.disconnect(self.featureDeleted)  #implement

            #           tLayer.layer().repaintRequested.disconnect(tLayer.repaintRequested)
            tLayer.layer().editingStarted.disconnect(tLayer.layerEditStarted)  # change to when layer is loaded also!
            tLayer.layer().editingStopped.disconnect(tLayer.layerEditStopped)
            tLayer.tearDown()


    def _writeMapLayer(self,layer,elem,doc):
        Log.debug("Write Map Layer")
        self.tearDownDocks(layer.id())

    def tearDownDocks(self,layerId = None):
        Log.debug("tearDownDocks")
        reopen = []
        for (lid,fid) in self._featureDocks.keys():
            if layerId is not None and lid != layerId:
                continue
            try:
                dock = self._featureDocks[(lid,fid)]
                Log.debug(dock)
                if dock and dock.isVisible():
                    Log.debug("Closing")
                    dock.saveGeometry()
                    reopen.append((lid,fid))
            except Exception as e:
                Log.debug(e)
        Settings.setp('featureDocks',json.dumps(reopen))

    def tearDown(self):
        
        self.tearDownDocks()
        self._iface.legendInterface().groupRelationsChanged.disconnect(self.legendRelationsChanged)
        self.tearDownTLayers()
        if 0:
            self._iface.legendInterface().removeLegendLayerAction(self.actions['config'])
            self._iface.legendInterface().removeLegendLayerAction(self.actions['pause'])
            self._iface.legendInterface().removeLegendLayerAction(self.actions['resume'])
        QgsProject.instance().readProject.disconnect(self.readProject)
        QgsProject.instance().layerLoaded.disconnect(self.layerLoaded)
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layerWillBeRemoved)
        self.lgd.clicked.disconnect(self.legendPressed)
        self.lgd.doubleClicked.disconnect(self.legendDblClicked)

        self._iface.legendInterface().currentLayerChanged.disconnect(
            self.currentLayerChanged)  # change to when layer is loaded also!
        self._iface.mapCanvas().renderStarting.disconnect(self.renderStarting)


    def __del__(self):
        pass


