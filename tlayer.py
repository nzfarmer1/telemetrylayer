# -*- coding: utf-8 -*-
"""
/***************************************************************************
  tLayer
  
  Layers are children of MQTT Client and of course represent a single QGIS layer
  
  Broker connetions are established when layer is visible

  ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4 import QtGui
from qgis.core import *
from qgis.utils import qgsfunction

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

                self.brokerFid      = int(Settings.getMeta('brokerId','fids'))
                self.nameFid        = int(Settings.getMeta('name','fids'))
                self.typeFid        = int(Settings.getMeta('type','fids'))
                self.topicFid       = int(Settings.getMeta('topic','fids'))
                self.payloadFid     = int(Settings.getMeta('payload','fids'))
                self.updatedFid     = int(Settings.getMeta('updated','fids'))
                self.changedFid     = int(Settings.getMeta('changed','fids'))
                self.connectedFid   = int(Settings.getMeta('connected','fids'))

                self._mutex = QMutex(0)
                self._values = {}
                self._dirty = False

                self.isEditing = False

                self._iface =  creator._iface
                self._paused = False
                self._fid  = None
                self._feat = None
                self._broker = None
                self._topicType = None
                self._topicManager = None
                

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

                Log.debug("tLayer _init__  LayerID = " + str(self._layer.id()) )
                self.updateConnected(False)
                

        def run(self):
                Log.debug("Running")
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
                            if topic != None:
                                Log.debug("Subscribitng " + topic)
                                self.subscribe(topic,1)
                self._layer.triggerRepaint()
                palyr = QgsPalLayerSettings() 
                palyr.readFromLayer(self.layer())
                exp =  palyr.getLabelExpression()          
               # Log.debug(exp.dump())



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
                _type = str(feat.attribute("type"))
                if zlib.crc32(_payload) == zlib.crc32(payload):
                        self.changeAttributeValue (feat.id(), self.updatedFid, int(time.time()),False)
                else:
                        fmt = self._topicManager.formatPayload(self._topicType,payload)
                        Log.status("Telemetry Layer " + self._broker.name() + ":" + self._layer.name() + ":" +  feat.attribute("name") + ": now " + fmt)
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


        def commitChanges(self):

            if not self._dirty:
                return

            try:
                if self._layer == None:
                    return

                if QgsApplication.activeWindow() == None \
                        or not 'QMainWindow' in str(QgsApplication.activeWindow()):
                      return
                    
#  Todo: Check for valid Layer!!!!
                if self.isEditing or self._layer.isReadOnly():
                        return

                with QMutexLocker(self._mutex):
                        if len(self._values) == 0:
                                return

                        self._layer.startEditing()
                        for key,val in self._values.iteritems():
                                fid,fieldId = key
                                self._layer.changeAttributeValue (fid, fieldId, val)

                        self._layer.commitChanges()
                        self._values.clear()
                        self._dirty = False
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

                self.addAttributes(pr)
                self.set(tLayer.LayerType,"true")
                self.set("BrokerId",broker.id())
                self.set("TopicType",topicType)
                Log.debug("Getting topic manager" + str(broker.topicManager()))
                self._topicManager.setFormatter(self._layer,topicType)
                self._layer.commitChanges()
                
                
                # Commit changes
                Log.debug("tLayer create")
                Log.debug(self._iface.legendInterface().isLayerVisible(self._layer))

        def addAttributes(self,pr):
                
                """
                function addAttributes(self,layer dataProvider) => void
                Default handler for adding attributes
                Sub class to add additional attributes

                # Todo
                # Set lengths
                # Set comments
                # Set key fields uneditable http://qgis.org/api/classQgsVectorLayer.html#aa1585c854a22d545111a3a32d717c02f

                """
                attributes = [ QgsField("brokerId",        QVariant.Int),
                                    QgsField("type",        QVariant.String),
                                    QgsField("name",        QVariant.String),
                                    QgsField("topic",       QVariant.String),
                                    QgsField("payload",     QVariant.String),
                                    QgsField("updated",     QVariant.Int),
                                    QgsField("changed",     QVariant.Int),
                                    QgsField("connected",   QVariant.Int)];
                
                        
                # Add Params
                pr.addAttributes( attributes )

              #  feat = QgsFeature()
              #  feat.setGeometry( QgsGeometry.fromPoint(QgsPoint(10,10)) )
              #  feat.setAttributes(["Broker Uptime","MQTT Property","$SYS/broker/uptime","",int(time.time()),int(time.time()),False])

               # pr.addFeatures([feat])

       # Respond to add Feature

        def beforeRollBack(self):
                Log.debug("before rollback")
                Log.debug(self._fid)
                self._layer.dataProvider().deleteFeatures([self._fid])
#        self._layer.destroyEditCommand()

        def addFeature(self,fid):
                Log.debug(self._fid)
                Log.debug(fid)
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
                    self._broker
                    feat.setAttributes([self._broker.id(),
                                        self._topicType,
                                        topic['name'],
                                        topic['topic'],
                                        "No updates",
                                        int(time.time()),
                                        int(time.time()),
                                        self.isRunning()])
                    # Add Params
    
                    self._layer.updateFeature(feat)
                    self._layer.commitChanges()
                    self._feat = feat
                except Exception as e:
                    Log.debug(e)
                    self._layer.deleteFeature(fid)
                    self._layer.commitChanges()
                    return None
                    
                return feat

        def setBroker(self,broker,updateFeatures = True):
            Log.debug("Updating broker object ")
            self._broker = broker # update broker object
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
        
        
        def _topicsUpdated(self):
                Log.debug("_topicsUpdated")
        
        def tearDown(self):
                Log.debug("tLayer Tear down")
                self._dirty = False # Don't commit any changes if we are being torn down
                self.stop()


