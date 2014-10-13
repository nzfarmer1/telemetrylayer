# -*- coding: utf-8 -*-
"""
/***************************************************************************
  tLayer
  
  Layers are children of MQTT Client and of course represent a single QGIS layer
  
  Broker connections are established when layer is visible

  ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4 import QtGui
from qgis.core import *
from qgis.gui import QgsAttributeDialog

from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from lib import mosquitto as Mosquitto
from tltopicmanagerfactory import tlTopicManagerFactory as topicManagerFactory
from tlbrokerconfig import tlBrokerConfig
from tlmqttclient import *
from tladdfeature import tlAddFeature as AddFeature
from tlbrokers import tlBrokers as Brokers,BrokerNotFound
import time,os, zlib



class tLayer(MQTTClient):

        LayerType = 'Telemetry'

        # AttributeIDs
        
        nameFid        = 0
        topicFid       = 1
        qosFid         = 2
        matchFid       = 3
        payloadFid     = 4
        updatedFid     = 5
        changedFid     = 6
        connectedFid   = 7
        visibleFid     = 8
        reservedFid    = 9



        # SIGNALS
        featureUpdated       = pyqtSignal(object,object)
        featureDialogClosed  = pyqtSignal(object)




        @staticmethod
        def isTLayer(  l ):
                if l == None:
                        return False
                if l.type() != QgsMapLayer.VectorLayer:
                        return False
                pr = l.dataProvider()
                if not pr or pr.name() != 'memory':
                        return False
                return l.customProperty(tLayer.LayerType,'false') == 'true'
                     
        @staticmethod
        def getBrokerId(l):
                return l.customProperty("BrokerId",-1)
                     
        def __init__(self,
                        creator,
                        layer = None,
                        broker = None,
                        topicType = None):


                self._layer = layer
                self._plugin_dir = creator._plugin_dir
                self._creator = creator
                self._dict ={}

                self._mutex = QMutex(0)
                self._values = {}
                self._dirty = False

                self.isEditing = False

                self._iface         = creator._iface
                self._paused        = False
                self._fid           = None
                self._feat          = None
                self._broker        = None
                self._topicType     = None
                self._topicManager  = None
                

                if broker != None and topicType !=None:
                   self.setBroker(broker,False) 
                   self._prepare(broker,topicType) # Add Layer properties for broker
                else:
                   _broker = Brokers.instance().find(self.get('BrokerId'))     
                   if _broker == None:
                        raise BrokerNotFound("No MQTT Broker found when loading Telemetry Layer " + self.layer().name())

                   self.setBroker(_broker)
                   self._topicType = self.get('TopicType')
                    
                super(tLayer,self).__init__(self,
                                            self._layer.id(), # Add randown
                                            self._broker.host(),
                                            self._broker.port(),
                                            self._broker.poll(),
                                            self._broker.keepAlive(),
                                            True)

                self.updateConnected(False)
                self.featureUpdated.connect(topicManagerFactory.featureUpdated) # Tell dialog box to update a feature
                self.layer().attributeValueChanged.connect(self.attributeValueChanged)
                
        def attributeValueChanged(self,  fid, idx, val):
            if fid < 0:
                return
#            Log.debug("Feature changed " + str(fid) + " "  + str(idx) + " "  + str(val) )

            if idx == self.topicFid:
                Log.debug("topic changed")
                request  = QgsFeatureRequest(fid)
                feat = next(self.layer().getFeatures(request),None)
                for topic in self._broker.topics(self._topicType):
                    if feat['topic'] == topic['topic']:
                       feat['name'] = topic['name']
                       feat['payload'] = 'No updates'
                       self._layer.startEditing()
                       self._layer.updateFeature(feat)
                       self._layer.commitChanges()
                       break
            
            if idx in [self.topicFid,self.qosFid] and self.isRunning():
                self.restart()
                

        def run(self):
                Log.debug("Running " + self.layer().name())
                self._dict ={}
                self._values = {}
                
                super(tLayer,self).run()
                

        def kill(self):
                super(tLayer,self).kill()


        def onConnect(self,mosq, obj, rc):
                self._dict = {}
                self.updateConnected(True)
                feat  = QgsFeature()
                iter = self._layer.getFeatures()
                while iter.nextFeature(feat):
                            topic = str(feat.attribute("topic"))
                            qos = int(feat.attribute("qos"))
                            if not qos in range(3):
                                Log.warn("Topic QoS must be beween 0 and 2")
                                continue
                            if topic != None:
                                Log.debug("Subscribing " + topic + " " + str(qos))
                                self.subscribe(topic,qos)
                self._layer.triggerRepaint()



        def onLog(self,mosq, obj, level, string):
                #Log.info(string)
                pass

        def onDisConnect(self,mosq, obj, rc):
                
                self.updateConnected(False)
                feat  = QgsFeature()
                iter = self._layer.getFeatures()
                while iter.nextFeature(feat):
                            topic = str(feat.attribute("topic"))
                            if topic != None:
                                Log.debug("Unsubscribe "+ topic)
                                self.unsubscribe(topic)
                self._layer.triggerRepaint()
                

        """
        Update values foreach topic:featureId

        """

        def onMessage(self,mq, obj, msg):
#                Log.status('TLayer Got ' + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
              
                try:
                        with QMutexLocker(self._mutex):
                                feat  = QgsFeature()
                                iter = self._layer.getFeatures()
                                while iter.nextFeature(feat):
                                        topic = str(feat.attribute("topic"))
                                        key = msg.topic + ':' + str(feat.id())
                                        if key in self._dict:
                                                self.updateFeature(feat,msg.topic,msg.payload)
                                        elif Mosquitto.topic_matches_sub(topic,msg.topic):
                                                self._dict[key] = feat.id()
                                                self.updateFeature(feat,msg.topic,msg.payload)

                        self._layer.triggerRepaint()

                except Exception as e:
                        Log.critical("MQTT Client - Error updating features! " + str(e))

        def updateFeature(self,feat,topic,payload):
            
                self._dirty = True
                _payload = str(feat.attribute("payload"))
                if zlib.crc32(_payload) == zlib.crc32(payload): # no change
                        self.changeAttributeValue (feat.id(), self.updatedFid, int(time.time()),False)
                else:
                        fmt = self._topicManager.formatPayload(self._topicType,payload)
                        Log.status("Telemetry Layer " + self._broker.name() + ":" + self._layer.name() + ":" +  feat.attribute("name") + ": now " + fmt)
                        self.changeAttributeValue (feat.id(), self.matchFid, topic,False)
                        self.changeAttributeValue (feat.id(), self.payloadFid, payload,False)
                        self.changeAttributeValue (feat.id(), self.updatedFid, int(time.time()),False)
                        self.changeAttributeValue (feat.id(), self.changedFid, int(time.time()),False)
                        

        def updateConnected(self,state):
                feat  = QgsFeature()
                iter = self._layer.getFeatures()
                while iter.nextFeature(feat):
                            self.changeAttributeValue (feat.id(), self.connectedFid, state,False)


        def changeAttributeValue(self,fid,fieldId,val,signal=False):
                key = (fid,fieldId)
                self._values[key] = val


        def brokerUpdated(self):
                topics = self._broker.topics(self._topicType)
                topicsmap = dict()
                for topic in topics:
                    topicsmap[topic['name']] = topic['topic']
                
                self._layer.setEditorWidgetV2Config(self.topicFid,topicsmap)


        def commitChanges(self):

            if not self._dirty:
                return

            try:
                if self._layer == None:
                    return
                
#                Log.debug(QgsApplication.activeWindow().centralWidget().windowTitle())

                if QgsApplication.activeWindow() == None \
                        or (
                                not 'QMainWindow' in str(QgsApplication.activeWindow()) \
                                and not QgsApplication.activeWindow().windowTitle() == 'Feature Attributes' # Paramaterise?
                           ):
                      return
                    
#  Todo: Check for valid Layer!!!!
                if self.isEditing or self._layer.isReadOnly():
                        return
                
                fids = []

                with QMutexLocker(self._mutex):
                        if len(self._values) == 0:
                                return

                        self._layer.startEditing()
                        for key,val in self._values.iteritems():
                                fid,fieldId = key
                                self._layer.changeAttributeValue (fid, fieldId, val)
                                if fid not in fids:
                                    fids.append(fid)

                        self._layer.commitChanges()
                        self._values.clear()
                        self._dirty = False
                for fid in fids:
                    request  = QgsFeatureRequest(fid)
                    feat = next(self.layer().getFeatures(request),None)
                    if feat !=None:
                        self.featureUpdated.emit(self,feat)

            except AttributeError:
                pass
            except Exception as e:
                Log.debug("Error committing " + str(e))
    
        def focusChange(self,Qw1,Qw2):
            if Log !=None:
                self.commitChanges()

        def layer(self):
                return self._layer

        def _prepare(self,broker,topicType):

                self._broker    = broker
                self._topicType = topicType
                pr = self._layer.dataProvider()

                # Enter editing mode
                self._layer.startEditing()

                # add fields

                self.set(tLayer.LayerType,"true")
                self.set("BrokerId",broker.id())
                self.set("TopicType",topicType)
                Log.debug("Getting topic manager" + str(broker.topicManager()))
                attributes = self.getAttributes() + \
                    self._topicManager.getAttributes(self.layer(),topicType)

                # Add Params
                
                pr.addAttributes( attributes )

                self._topicManager.setFormatter(self._layer,topicType)
                self._layer.commitChanges()

                # Configure Attributes
                
                for i in range(9):
                    self._layer.setEditorWidgetV2(i,'Hidden')

                

                self._layer.setEditorWidgetV2(self.topicFid,'ValueMap')
                self.brokerUpdated()
                
                self._layer.setEditorWidgetV2(self.qosFid,'ValueMap')
                self._layer.setEditorWidgetV2Config(self.qosFid,{u'QoS0':0,u'QoS1':1,u'QoS2':2})
              
                self._layer.setEditorWidgetV2(self.visibleFid,'ValueMap')
                self._layer.setEditorWidgetV2Config(self.visibleFid,{"True":1,"False":0})
                
                
                #self._layer.setEditorWidgetV2(self.topicFid,'ValueMap')
                
                
                
                # Commit changes
                Log.debug("tLayer create")
                Log.debug(self._iface.legendInterface().isLayerVisible(self._layer))

        def getAttributes(self):
                
                """
                function getAttributes(self,layer dataProvider) => void
                Default handler for adding attributes

                # Todo
                # Set lengths
                # Set comments
                # Set key fields uneditable http://qgis.org/api/classQgsVectorLayer.html#aa1585c854a22d545111a3a32d717c02f

                """
                attributes = [      QgsField("name",        QVariant.String, "Feature Name",0,0,"Name of Sensor/Device/Topic"),
                                    QgsField("topic",       QVariant.String, "MQTT Topic",0,0,"Topic path"),
                                    QgsField("qos",         QVariant.Int   , "MQTT QoS",1,0,"Quality of Service"),
                                    QgsField("match",       QVariant.String, "Topic Match",0,0,"When topics are patterns, this field contains the actual match"),
                                    QgsField("payload",     QVariant.String, "MQTT Payload",0,0,"Payload data returned from MQTT broker"),
                                    QgsField("updated",     QVariant.Int   , "Time since last Update",12,0,"Native value stored as POSIX (UTC) Time"),
                                    QgsField("changed",     QVariant.Int   , "Time since last Change",12,0, "Native value stored as POSIX (UTC) Time"),
                                    QgsField("connected",   QVariant.Int   , "Broker is connected",1,0, "Valid only for visible layers"),
                                    QgsField("visible",     QVariant.Int   , "Visible",1,0,"Feature is visible and can be rendered. Invisible layers available via Features Tab under Broker")];
                
                return attributes
  
              #  feat = QgsFeature()
              #  feat.setGeometry( QgsGeometry.fromPoint(QgsPoint(10,10)) )
              #  feat.setAttributes(["Broker Uptime","MQTT Property","$SYS/broker/uptime","",int(time.time()),int(time.time()),False])

               # pr.addFeatures([feat])
               

       # Respond to add Feature

        def beforeRollBack(self):
            pass    
  #              Log.debug("before rollback")
 #               Log.debug(self._fid)
#                self._layer.dataProvider().deleteFeatures([self._fid])
#        self._layer.destroyEditCommand()

        def addFeature(self,fid):
                if (fid < 0 and self._fid != fid):
                        self._fid = fid
                elif (fid >0 or fid == self._fid):
                        # handle roll back
                        #self._fid = None
                        return None
                    
                # Look Up broker and topicType

                feat = QgsFeature(fid)
                try:
                    tlAddFeature  = AddFeature(self._broker,self._topicType)
                    result = tlAddFeature.exec_()
                    if result == 0:
                            self._layer.deleteFeature(fid)
                            self._layer.commitChanges()
                            return None
    
                    topic = tlAddFeature.getTopic()

                    if  not 'qos' in topic:
                        topic['qos'] = 0
                    
                    if  not 'visible' in topic:
                        topic['visible'] = True
                        
                    
                    feat.setAttributes([topic['name'],
                                        topic['topic'],
                                        topic['qos'],
                                        topic['topic'], # gets updated with topic
                                        "No updates",
                                        int(time.time()),
                                        int(time.time()),
                                        self.isRunning(),
                                        topic['visible']])
                    # Add Params
    
                    self._layer.updateFeature(feat)
                    self._layer.commitChanges()
                    self._feat = feat
                except Exception as e:
                    Log.debug(e)
                    self._layer.deleteFeature(fid)
                    self._layer.commitChanges()
                    return None
                finally:
                    pass
                    
                return feat

        def setBroker(self,broker,updateFeatures = True):
            Log.debug("Updating broker object ")
            self._broker = broker # update broker object
            self.setPoll(broker.poll())
            self.setHost(broker.host())
            self.setPort(broker.port())
            self.setKeepAlive(broker.keepAlive())
            self._topicManager = topicManagerFactory.getTopicManager(broker)
            
            # Todo:
            # For each topic
            # Find features with feat.attrib[topic] == topic
            # Update params
 
        def getBroker(self):
            return self._broker

        def get(self,key,default = None):
                      result = self._layer.customProperty(key)
                      if result ==None:
                                return default
                      return str(result)

        def set(self,key,value):
                      self._layer.setCustomProperty(key,value)

        def setPaused(self,state):
                self._paused = state

        def isPaused(self):
                return self._paused

        def resume(self):

                if self.isRunning() == False:
                        Log.progress("Starting client")
                        self.run()


        def pause(self):
                if self.isRunning() == True:
                        Log.debug("Stopping client")
                        self.kill()

        def refresh(self,state):
                self.commitChanges()
                if state:
                        self.resume()
                else:
                        self.pause()

        def layerEditStarted(self):
                self.isEditing = True

        def layerEditStopped(self):
                self.isEditing = False

        def topicManager(self):
                return topicManagerFactory.getTopicManager(self._broker)

        def topicType(self):
                return self._topicType
        
        
        def tearDown(self):
                Log.debug("tLayer Tear down")
                self.featureUpdated.disconnect(topicManagerFactory.featureUpdated)
                self.layer().attributeValueChanged.disconnect(self.attributeValueChanged)

                self._dirty = False # Don't commit any changes if we are being torn down
                self.stop()


