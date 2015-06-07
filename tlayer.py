# -*- coding: utf-8 -*-
"""
/***************************************************************************
  tLayer
  
  Layers are children of MQTT Client and represent a single QGIS layer
  
  Broker connections are established when layer is visible

  ***************************************************************************/
"""

from PyQt4.QtXml import *

from PyQt4.QtCore import *
from PyQt4 import QtGui
from qgis.core import *

from lib.tlsettings import tlSettings as Settings, tlConstants as Constants
from lib.tllogging import tlLogging as Log
from lib import mosquitto as Mosquitto
from tltopicmanagerfactory import tlTopicManagerFactory as topicManagerFactory
from tlbrokerconfig import tlBrokerConfig
from tlmqttclient import *
from telemetrylayer import TelemetryLayer as telemetryLayer
from tladdfeature import tlAddFeature as AddFeature
from tlbrokers import tlBrokers as Brokers, BrokerNotFound, BrokerNotSynced, BrokersNotDefined
import time, os, zlib
import Queue as Queue

#import resource


class tLayer(MQTTClient):
    """
    tLayer provides an interface between a Layer, and the MQTT Client.
    It takes care of
    - starting the broker comms;
    - subscribing to topics;
    - refreshing the features
    
    """

    kLayerType      = 'tlayer/Telemetry'
    kBrokerId       =  'tlayer/brokerid'
    kTopicManager   = 'tlayer/topicManager'
    kQueueSize      = 100


    # SIGNALS
    featureUpdated = pyqtSignal(object, object)
    

    @staticmethod
    def isTLayer(l):
        if l is None:
            return False
        if l.type() != QgsMapLayer.VectorLayer:
            return False
        pr = l.dataProvider()
        if not pr or pr.name() != 'memory':
            return False
        return l.customProperty(tLayer.kLayerType, 'false') == 'true'

    @staticmethod
    def getBrokerId(l):
        return l.customProperty(tLayer.kBrokerId, -1)

    def brokerId(self):
        return self.getBrokerId(self._layer)

    def __init__(self,
                 creator,
                 layer=None,
                 broker=None,
                 topicManager=None):

        self._layer = layer
        self._plugin_dir = creator._plugin_dir
        self._creator = creator
        self._dict = {}

        self._mutex  = QMutex(0)
        self._values = {}
        self.Q       = Queue.Queue(self.kQueueSize)
        self._dirty  = False
        self.establishedFeatures = []
        self.restartScheduled = False
 
        self.isEditing = False

        self._iface     = creator._iface
        self._paused    = False
        self._fid       = None
        self._feat      = None
        self._broker    = None
        self._topicType = None
        self._topicManager = None
        self._formattersSet = False
            
        if broker is not None and topicManager is not None:
            self.setBroker(broker, False)
            if not self.isTLayer(self._layer):
                self._prepare(broker, topicManager)  # Add Layer properties for broker
        else:
            _broker = Brokers.instance().find(self.get(self.kBrokerId))
            if _broker is None:
                raise BrokerNotFound("No MQTT Broker found when loading Telemetry Layer " + self.layer().name())

            self.setBroker(_broker)
            #self._setFormatters()

        super(tLayer, self).__init__(self,
                                     self._layer.id(),  # Add randown
                                     self._broker,
                                     True)

        self.updateConnected(False)
        self._broker.deletingBroker.connect(self.tearDown)
        self.featureUpdated.connect(topicManagerFactory.featureUpdated)  # Tell dialog box to update a feature
        self.layer().attributeValueChanged.connect(self.attributeValueChanged)


    def attributeValueChanged(self, fid, idx, val):
        if fid < 0:
            return

        # Scheduled restarts not stable. Need to check if process is in start/stop phase
#        if idx in [Constants.topicIdx, Constants.qosIdx] and self.isRunning():
#           self.restartScheduled = True


    def run(self):
        if not self._canRun():
            return

        Log.debug("Running " + self.layer().name())

        self._setFormatters(True)
        self._dict = {}
        self._values = {}
        self.Q.queue.clear()

        super(tLayer, self).run()


    def kill(self):
        super(tLayer, self).kill()

    def stop(self):
        super(tLayer, self).stop()
        try:
            iter = self._layer.getFeatures()
            if iter.next():
                self.triggerRepaint()
        except Exception as e: #if the broker is deleted, the layer has been removed - don't repaint
            Log.debug(e)


    def onConnect(self, mosq, obj, rc):
        # Log.debug(self._layer.rendererV2().dump())

        self._dict = {}
        self.updateConnected(True)
        for feat in self._layer.getFeatures():
            if feat.id() < 0:
                continue
            try:
                topic = str(feat.attribute("topic"))
                qos = int(feat.attribute("qos"))
            
                if not qos in range(3):
                    Log.warn("Topic QoS must be beween 0 and 2")
                    continue
    
                if topic is not None:
                    self.subscribe(topic, qos)
                else:
                    Log.critical("Invalid topic")
                   
            except TypeError:
                Log.debug("Error adding features from layer")
                pass
                
        self.triggerRepaint()


    def onLog(self, mosq, obj, level, string):
        # Log.info(string)
        pass

    def onDisConnect(self, mosq, obj, rc):

        for feat in self._layer.getFeatures():
            topic = str(feat.attribute("topic"))
            if topic is not None:
                self.unsubscribe(topic)
        self.updateConnected(False)
        self.triggerRepaint()


    """
    Update values foreach topic:featureId

    """

    def onMessage(self, mq, obj, msg):
        Log.debug('Got ' + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        if not self.Q.full():
            self.Q.put(msg)
            self._processQueue() # sets dirty flag as req.
            self.triggerRepaint()
    
    def _processQueue(self):
        if self.Q.empty():
            return
        try:
            while(not self.Q.empty() and not self._isEditing()):
                msg =self.Q.get() 
                for feat in self._layer.getFeatures():
                    topic = str(feat.attribute("topic"))
                    key = msg.topic + ':' + str(feat.id())
                    with QMutexLocker(self._mutex):
                        if key in self._dict:
                            self.updateFeature(feat, msg.topic, msg.payload)
                        elif Mosquitto.topic_matches_sub(topic, msg.topic):
                            self._dict[key] = feat.id()
                            self.updateFeature(feat, msg.topic, msg.payload)

        except Queue.Empty:
            Log.debug("Empty Queue")
            return

        except Exception as e:
            Log.critical("MQTT Client - Error updating features! " + str(e))


    def updateFeature(self, feat, topic, payload):
        _payload = str(feat.attribute("payload"))
        if zlib.crc32(_payload) == zlib.crc32(payload):  # no change
            self.changeAttributeValue(feat.id(), Constants.updatedIdx, int(time.time()), False)
        else:
            self._dirty = True # don't trigger refresh or commit changes if payload unchanged
            # note: this is a tradeoff - less screen refreshes, but less accurate timestamps
            self.changeAttributeValue(feat.id(), Constants.payloadIdx, payload, False)
            self.changeAttributeValue(feat.id(), Constants.matchIdx, topic, False)
            self.changeAttributeValue(feat.id(), Constants.updatedIdx, int(time.time()), False)
            self.changeAttributeValue(feat.id(), Constants.changedIdx, int(time.time()), False)


    def updateConnected(self, state):
        for feat in self._layer.getFeatures():
            self.changeAttributeValue(feat.id(), Constants.connectedIdx, state, False)


    def changeAttributeValue(self, fid, idx, val, signal=False):
        key = (fid, idx)
        self._values[key] = val
        self._dirty = True



    def commitChanges(self):
        self._processQueue()

        if not self._dirty or self._isEditing():
            return

        try:
            fids = []
            with QMutexLocker(self._mutex):

                if len(self._values) == 0:
                    return
                
                self._layer.startEditing()
                self.topicManager().beforeCommit(self,self._values)

                for key, val in self._values.iteritems():
                    fid, fieldId = key
                    self._layer.changeAttributeValue(fid, fieldId, val)
                    if fid not in fids:
                        fids.append(fid)

                self._layer.commitChanges()
                self._values.clear()
                self._dirty = False
            for fid in fids:
                request = QgsFeatureRequest(fid)
                feat = next(self.layer().getFeatures(request), None)
                if feat is not None:
                    self.featureUpdated.emit(self, feat)

        except AttributeError:
            pass
        except Exception as e:
            Log.debug("Error committing " + str(e))


    def focusChange(self, Qw1, Qw2):
        if Log is not None:
            self.commitChanges()

    def layer(self):
        return self._layer

    def _prepare(self, broker, topicManager):

        self._broker = broker
        pr = self._layer.dataProvider()

        # Enter editing mode
        self._layer.startEditing()

        # add fields

        self.set(self.kLayerType, "true")
        self.set(self.kBrokerId, broker.id())
        self.set(self.kTopicManager, topicManager.id())

        attributes = self.getAttributes() + \
                     topicManager.getAttributes()

        # Add Params

        pr.addAttributes(attributes)

        self._layer.commitChanges()
        self._setFormatters()
        self._iface.legendInterface().setCurrentLayer(self._layer)
    
     
    def _setFormatters(self,update = False ): # change to bitmask


        if self._formattersSet:
            return
        else:
            self._formattersSet = True

        # Configure Attributes
        self._layer.startEditing()

        for i in range(Constants.reservedIdx+1):
            self._layer.setEditorWidgetV2(i, 'Hidden')

        self._layer.setEditorWidgetV2(Constants.qosIdx, 'ValueMap')
        self._layer.setEditorWidgetV2Config(Constants.qosIdx, {u'QoS0': 0, u'QoS1': 1, u'QoS2': 2})

        self._layer.setEditorWidgetV2(Constants.visibleIdx, 'ValueMap')
        self._layer.setEditorWidgetV2Config(Constants.visibleIdx, {"True": 1, "False": 0})

#        self._layer.setEditorWidgetV2(Constants.topicIdx, 'Immutable')

        self._layer.commitChanges()

        if not update:
    
            self._layer.startEditing()
            self.topicManager().setLayerStyle(self._layer)
            self._layer.commitChanges()

            self._layer.startEditing()
            self.topicManager().setLabelFormatter(self._layer)
            self._layer.commitChanges()
            
        self._layer.startEditing()
        self.topicManager().setEditorWidgetsV2(self._layer)
        self._layer.commitChanges()
        
#        self._layer.startEditing()
#        self._topicManager.instance(self.topicType()).setFeatureForm(self._layer)
#        self._layer.commitChanges()
        

    def getAttributes(self):

        """
        function getAttributes(self) => array of attributes
        Default handler for adding attributes

        """
 
        attributes = [QgsField("name", QVariant.String, "Feature Name", 0, 0, "Name of Sensor/Device/Topic"),
                      QgsField("topic", QVariant.String, "MQTT Topic", 0, 0, "Topic path"),
                      QgsField("qos", QVariant.Int, "MQTT QoS", 1, 0, "Quality of Service"),
                      QgsField("match", QVariant.String, "Topic Match", 0, 0,
                               "When topics are patterns, this field contains the actual match"),
                      QgsField("payload", QVariant.String, "MQTT Payload", 0, 0,
                               "Payload data returned from MQTT broker"),
                      QgsField("updated", QVariant.Int, "Time since last Update", 12, 0,
                               "Native value stored as POSIX (UTC) Time"),
                      QgsField("changed", QVariant.Int, "Time since last Change", 12, 0,
                               "Native value stored as POSIX (UTC) Time"),
                      QgsField("connected", QVariant.Int, "Broker is connected", 1, 0, "Valid only for visible layers"),
                      QgsField("visible", QVariant.Int, "Visible", 1, 0,
                               "Feature is visible and can be rendered. Invisible layers available via Features Tab under Broker"),
                      QgsField("context", QVariant.String, "Context", 0, 0,
                               "Context of label renderer - i.e. map, feature-list, dock-title,dock-content")]

        return attributes

    def beforeRollBack(self):
        self._layer.destroyEditCommand() # Add this?
 
    def applyFeature(self,feature):
        found = False
        for feat in self.establishedFeatures:
            if feat['topic'] == feature['topic']:
                found = True
                break
        if not found:
            Log.debug("No feature to Apply")
            return

        try:
            fmap = self._layer.dataProvider().fieldNameMap()
            fmax = self._layer.dataProvider().fieldNameIndex("context")

            for key,fieldId in fmap.iteritems():
                if key in ['qos','visible'] or fieldId > fmax:
                #   Log.debug("changing value " + key + " " + str(feat[key]) + " to " + str(feature[key]))
                   self._layer.changeAttributeValue(feat.id(), fieldId, feature[key])
            self._layer.deleteFeature(feature.id())
            self._layer.commitChanges()
        except Exception as e:
            Log.debug("Error applying feature " + str(e))
        

    def addFeature(self, fid):
        Log.debug("add Feature")
        if fid < 0 and not self._fid:
            self._fid = fid
        elif fid >= 0 or fid == self._fid:
            # handle roll back
            #self._fid = None
            return None

        # Look Up broker and topicType

        feat = QgsFeature(fid)
        try:
            telemetryLayer.instance().checkBrokerConfig()
            tlAddFeature = AddFeature(self.topicManager())
            result = tlAddFeature.exec_()
            if result == 0:
                self._layer.deleteFeature(fid)
                self._layer.commitChanges()
                return None

            topic   = tlAddFeature.getTopic()
            visible = tlAddFeature.getVisible()
            qos     = tlAddFeature.getQoS()
            
            attrs = [topic['name'],
                    topic['topic'],
                    qos,
                    topic['topic'],  # gets updated with topic
                    "No updates",
                    int(time.time()),
                    int(time.time()),
                    self.isRunning(),
                    visible,
                    'map']
            
            # merge with custom attributes
            feat.setAttributes(self.topicManager().setAttributes(self._layer,attrs))

            self._layer.updateFeature(feat)
            self._layer.commitChanges()
            self._feat = feat
        except BrokerNotSynced:
            Log.progress("Please save any unsaved Broker confugurations first")
            self._layer.deleteFeature(fid)
            self._layer.commitChanges()
        except BrokersNotDefined:
            Log.progress("You have no Brokers defined")
            self._layer.deleteFeature(fid)
            self._layer.commitChanges()
        except Exception as e:
            Log.debug(e)
            self._layer.deleteFeature(fid)
            self._layer.commitChanges()
            return None
        finally:
            pass

        return feat

    def setBroker(self, broker, updateFeatures=True):
        self._broker = broker  # update broker object
        self.setPoll(broker.poll())
        self.setHost(broker.host())
        self.setPort(broker.port())
        self.setKeepAlive(broker.keepAlive())

    def getBroker(self):
        return self._broker

    def get(self, key, default=None):
        result = self._layer.customProperty(key)
        if result is None:
            return default
        return str(result)

    def set(self, key, value):
        self._layer.setCustomProperty(key, value)

    def setPaused(self, state):
        self._paused = state

    def isPaused(self):
        return self._paused

    def resume(self):
        if self._canRun() and not self.isRunning():
            Log.progress("Starting MQTT client for " + self._broker.name() + " -> " + self.layer().name())
            self.run()

    def pause(self):
        if self.isRunning():
            Log.debug("Stopping client")
            self.kill()

    def refresh(self, state):
        if self._canRun():
            self.commitChanges()

# This is evil.  We need to capture the state between starting and running first!        
#        if state and self.restartScheduled and self.isRunning():
#            self.restartScheduled = False
#            self.restart()
#            return

        if state:
            self.resume()
        else:
            self.pause()


    def triggerRepaint(self):
#        if 'QDialog' in str( QgsApplication.activeWindow()): # Avoid nasty surprises
#            pass
        # Add additional checks?
#        else:
        if self._dirty or not self.Q.empty():
            self._layer.triggerRepaint()
 
    def layerEditStarted(self):
        self.establishedFeatures = []
        for feat in self._layer.getFeatures():
            self.establishedFeatures.append( feat )

        self.isEditing = True

    def layerEditStopped(self):
        self.establishedFeatures = []
        self.isEditing = False
#        if self.restartScheduled:
        self.triggerRepaint()

        
    def topicManager(self):
        return topicManagerFactory.getTopicManagerById(self.get(self.kTopicManager))

    def topicType(self):
        return self._topicType

    def _isEditing(self):
        return  (self.isEditing or self._layer.isReadOnly())

    def _canRun(self):
        return  self._hasFeatures() and not self._isEditing()

    def _hasFeatures(self):
        return self._layer.getFeatures() is not None

    def tearDown(self):
        Log.debug("Tear down TLayer")
        self.featureUpdated.disconnect(topicManagerFactory.featureUpdated)
        self.layer().attributeValueChanged.disconnect(self.attributeValueChanged)
       
        self._dirty = False  # Don't commit any changes if we are being torn down
        self.stop()
        


