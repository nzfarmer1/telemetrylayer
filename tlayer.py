# -*- coding: utf-8 -*-
"""
/***************************************************************************
  tLayer
  
  Layers are children of MQTT Client and of course represent a single QGIS layer
  
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
#import resource


class tLayer(MQTTClient):
    """
    tLayer provides an interface between a Layer, and the MQTT Client.
    It takes care of
    - starting the broker comms;
    - subscribing to topics;
    - refreshing the features
    
    """

    kLayerType = 'tlayer/Telemetry'
    kBrokerId = 'tlayer/brokerid'
    kTopicType = 'tlayer/topictype'


    # SIGNALS
    featureUpdated = pyqtSignal(object, object)
    featureDialogClosed = pyqtSignal(object)  # Hmm should be a SLOT?


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
                 topicType=None):

        self._layer = layer
        self._plugin_dir = creator._plugin_dir
        self._creator = creator
        self._dict = {}

        self._mutex = QMutex(0)
        self._values = {}
        self._dirty = False
        # self._topicChanged= []

        self.isEditing = False

        self._iface = creator._iface
        self._paused = False
        self._fid = None
        self._feat = None
        self._broker = None
        self._topicType = None
        self._topicManager = None

        if broker is not None and topicType is not None:
            self.setBroker(broker, False)
            self._prepare(broker, topicType)  # Add Layer properties for broker
        else:
            _broker = Brokers.instance().find(self.get(self.kBrokerId))
            if _broker is None:
                raise BrokerNotFound("No MQTT Broker found when loading Telemetry Layer " + self.layer().name())

            self.setBroker(_broker)
            self._topicType = self.get(self.kTopicType)

            #self._setFormatters()

        super(tLayer, self).__init__(self,
                                     self._layer.id(),  # Add randown
                                     self._broker,
                                     True)

        self.updateConnected(False)
        self._broker.deletingBroker.connect(self.tearDown)
        self.featureUpdated.connect(topicManagerFactory.featureUpdated)  # Tell dialog box to update a feature
        self.layer().attributeValueChanged.connect(self.attributeValueChanged)
        #self.brokerUpdated()

    def attributeValueChanged(self, fid, idx, val):
        if fid < 0:
            return

        if idx == Constants.topicIdx:
            Log.debug("topic changed")
        if idx in [Constants.topicIdx, Constants.qosIdx] and self.isRunning():
            self.restart()  # Enqueue?


    def run(self):
        if not self._canRun():
            return
        Log.debug("Running " + self.layer().name())
        self._dict = {}
        self._values = {}

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
        feat = QgsFeature()
        iter = self._layer.getFeatures()
        while iter.nextFeature(feat):
            if feat.id() < 0:
                continue
            try:
                topic = str(feat.attribute("topic"))
                qos = int(feat.attribute("qos"))
            
                if not qos in range(3):
                    Log.warn("Topic QoS must be beween 0 and 2")
                    continue
    
                # If the topic has changed, we need to update the name
                # (and perhaps additional properties for the layer)
                # This code is a little redundant as we're not
                # checking for topic change - however, it is not
                # called often and uses our own self.changeAttributeValue
                # method so the overhead is very small
    
                if topic is not None:
                    _topic = self._broker.topic(topic)
                    if _topic is not None:
                        self.changeAttributeValue(feat.id(), Constants.nameIdx, _topic['name'])
                        Log.debug("Subscribing " + topic + " " + str(qos))
                        self.subscribe(topic, qos)
                    else:
                        Log.critical("Updated topic " + topic + " not found! Please refresh your topic manager then re add the feature")
                        #self._layer.startEditing()
                        #self._layer.deleteFeature(feat.id())
                        #self._layer.commitChanges()
                   
            except TypeError:
                Log.debug("Error adding features from layer")
                pass
                
        self.triggerRepaint()


    def onLog(self, mosq, obj, level, string):
        # Log.info(string)
        pass

    def onDisConnect(self, mosq, obj, rc):

        feat = QgsFeature()
        iter = self._layer.getFeatures()
        while iter.nextFeature(feat):
            topic = str(feat.attribute("topic"))
            if topic is not None:
                Log.debug("Unsubscribe " + topic)
                self.unsubscribe(topic)
        self.updateConnected(False)
        self.triggerRepaint()


    """
    Update values foreach topic:featureId

    """

    def onMessage(self, mq, obj, msg):
        # Log.status('TLayer Got ' + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        
        try:
            with QMutexLocker(self._mutex):
                feat = QgsFeature()
                iter = self._layer.getFeatures()
                while iter.nextFeature(feat):
                    topic = str(feat.attribute("topic"))
                    key = msg.topic + ':' + str(feat.id())
                    if key in self._dict:
                        self.updateFeature(feat, msg.topic, msg.payload)
                    elif Mosquitto.topic_matches_sub(topic, msg.topic):
                        self._dict[key] = feat.id()
                        self.updateFeature(feat, msg.topic, msg.payload)

            #Log.debug("Triggering repaint")
            self.triggerRepaint()

        except Exception as e:
            Log.critical("MQTT Client - Error updating features! " + str(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.debug(repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback)))

    def updateFeature(self, feat, topic, payload):
        self._dirty = True
        _payload = str(feat.attribute("payload"))
        if zlib.crc32(_payload) == zlib.crc32(payload):  # no change
            self.changeAttributeValue(feat.id(), Constants.updatedIdx, int(time.time()), False)
        else:
            fmt = self._topicManager.instance(self.topicType()).formatPayload(payload)
            Log.status("Telemetry Layer " + self._broker.name() + ":" + self._layer.name() + ":" + feat.attribute(
                "name") + ": now " + fmt)
            self.changeAttributeValue(feat.id(), Constants.payloadIdx, payload, False)
            self.changeAttributeValue(feat.id(), Constants.matchIdx, topic, False)
            self.changeAttributeValue(feat.id(), Constants.updatedIdx, int(time.time()), False)
            self.changeAttributeValue(feat.id(), Constants.changedIdx, int(time.time()), False)


    def updateConnected(self, state):
        feat = QgsFeature()
        iter = self._layer.getFeatures()
        while iter.nextFeature(feat):
            self.changeAttributeValue(feat.id(), Constants.connectedIdx, state, False)


    def changeAttributeValue(self, fid, idx, val, signal=False):
        key = (fid, idx)
        self._values[key] = val
        self._dirty = True


    def brokerUpdated(self):
        topics = self._broker.topics(self._topicType)
        topicmap = dict()
        for topic in topics:
            if not topic['name'] in topicmap:  # there shouldn't be dups!
                topicmap[topic['name']] = topic['topic']
        self._layer.setEditorWidgetV2Config(Constants.topicIdx, topicmap)


    def commitChanges(self):
        #Log.debug("Committing"  + str( QgsApplication.activeWindow()))
        if not self._dirty:
            return
        
        try:
            if self._layer is None:
                return
            
            #                Log.debug(QgsApplication.activeWindow().centralWidget().windowTitle())

            #if QgsApplication.activeWindow() is None:
            #is None \
            #        or (
            #                    not 'QMainWindow' in str(QgsApplication.activeWindow())
            #                and not QgsApplication.activeWindow().windowTitle() == 'Feature Attributes'
            #                    # Paramaterise?
            #        ):
            #    return

            #  Todo: Check for valid Layer!!!!
            if self.isEditing or self._layer.isReadOnly():
                return

            fids = []

            with QMutexLocker(self._mutex):

                if len(self._values) == 0:
                    return
                

                self._layer.startEditing()
                self._topicManager.instance(self.topicType()).beforeCommit(self,self._values)

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

    def _prepare(self, broker, topicType):

        self._broker = broker
        self._topicType = topicType
        pr = self._layer.dataProvider()

        # Enter editing mode
        self._layer.startEditing()

        # add fields

        self.set(self.kLayerType, "true")
        self.set(self.kBrokerId, broker.id())
        self.set(self.kTopicType, topicType)
        attributes = self.getAttributes() + \
                     self._topicManager.instance(topicType).getAttributes()

        # Add Params

        pr.addAttributes(attributes)

        self._layer.commitChanges()
        self._setFormatters()
        self._iface.legendInterface().setCurrentLayer(self._layer)

    def _setFormatters(self):

        # Configure Attributes
        self._layer.startEditing()

        for i in range(Constants.reservedIdx):
            self._layer.setEditorWidgetV2(i, 'Hidden')

        self._layer.setEditorWidgetV2(Constants.qosIdx, 'ValueMap')
        self._layer.setEditorWidgetV2Config(Constants.qosIdx, {u'QoS0': 0, u'QoS1': 1, u'QoS2': 2})

        self._layer.setEditorWidgetV2(Constants.visibleIdx, 'ValueMap')
        self._layer.setEditorWidgetV2Config(Constants.visibleIdx, {"True": 1, "False": 0})

        self._layer.setEditorWidgetV2(Constants.topicIdx, 'ValueMap')
        self.brokerUpdated()

        self._layer.commitChanges()

        self._layer.startEditing()
        self._topicManager.instance(self.topicType()).setLayerStyle(self._layer)
        self._layer.commitChanges()
        self._layer.startEditing()
        self._topicManager.instance(self.topicType()).setFeatureForm(self._layer)
        self._layer.commitChanges()
        self._layer.startEditing()
        self._topicManager.instance(self.topicType()).setLabelFormatter(self._layer)
        self._layer.commitChanges()

    def getAttributes(self):

        """
        function getAttributes(self) => array of attributes
        Default handler for adding attributes

        # Todo
        # Set lengths
        # Set comments
        # Set key fields uneditable http://qgis.org/api/classQgsVectorLayer.html#aa1585c854a22d545111a3a32d717c02f

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
                      QgsField("reserved", QVariant.Int, "Reserved", 1, 0,
                               "Reserved for future use")]

        return attributes

    def beforeRollBack(self):
        self._layer.destroyEditCommand() # Add this?
        pass

        # Log.debug("before rollback")

    #               Log.debug(self._fid)
    #                self._layer.dataProvider().deleteFeatures([self._fid])
    #        self._layer.destroyEditCommand()

    def addFeature(self, fid):
        Log.debug("add Feature")
        if 0 > fid and not self._fid:
            self._fid = fid
        elif fid > 0 or fid == self._fid:
            # handle roll back
            #self._fid = None
            return None

        # Look Up broker and topicType


        feat = QgsFeature(fid)
        try:
            telemetryLayer.instance().checkBrokerConfig()
            tlAddFeature = AddFeature(self._broker, self._topicType)
            result = tlAddFeature.exec_()
            if result == 0:
                self._layer.deleteFeature(fid)
                self._layer.commitChanges()
                return None

            topic = tlAddFeature.getTopic()
            visible = tlAddFeature.getVisible()
            qos = tlAddFeature.getQoS()

            feat.setAttributes([topic['name'],
                                topic['topic'],
                                qos,
                                topic['topic'],  # gets updated with topic
                                "No updates",
                                int(time.time()),
                                int(time.time()),
                                self.isRunning(),
                                visible])
            # Add Params

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
        self._topicManager = topicManagerFactory.getTopicManager(broker)
        #if updateFeatures:
        #    self.brokerUpdated()

        # Todo:
        # For each topic
        # Find features with feat.attrib[topic] == topic
        # Update params

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
        if state:
            self.resume()
        else:
            self.pause()


    def triggerRepaint(self):
        if 'QDialog' in str( QgsApplication.activeWindow()): # Avoid nasty surprises
        
            # Log.debug("triggerRepaint"  + str( QgsApplication.activeWindow()))
            pass
        # Add additional checks?
        else:
            self._layer.triggerRepaint()

    def layerEditStarted(self):
        self.isEditing = True

    def layerEditStopped(self):
        self.isEditing = False

    def topicManager(self):
        return topicManagerFactory.getTopicManager(self._broker)

    def topicType(self):
        return self._topicType

    def _canRun(self):
        return  self._hasFeatures() and not (self.isEditing or self._layer.isReadOnly())

    def _hasFeatures(self):
        feat = QgsFeature()
        count = 0
        iter = self._layer.getFeatures()
        while count == 0 and iter.nextFeature(feat):
            if feat.id() > 0:
                count += 1
        return count > 0

    def tearDown(self):
        Log.debug("Tear down TLayer")
        self.featureUpdated.disconnect(topicManagerFactory.featureUpdated)
        self.layer().attributeValueChanged.disconnect(self.attributeValueChanged)
       
        self._dirty = False  # Don't commit any changes if we are being torn down
        self.stop()
        


