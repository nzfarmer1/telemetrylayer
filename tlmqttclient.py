"""
/***************************************************************************
 tlMQTTClient
 
 Wrapper for Mosquitto client with child handlers for one off activites
 like SingleShot requests

 ***************************************************************************/
"""

import sys
from PyQt4 import QtCore
from PyQt4.QtCore import QTimer, QThread, QObject, SIGNAL

from lib import mosquitto
#import paho.mqtt.client as paho
import sys
import traceback
import socket
from socket import error as socket_error
from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log

    # TODO
    # Add eExceptions for 32 Broke Pioe and 54 Connection Reset by Peer

class MQTTClient(QtCore.QObject):

    kMaxAttempts  = 3
    kMinKeepAlive = 5

    mqttOnConnect       = SIGNAL('mqttOnConnect(QObject,QObject,QObject)')
    mqttOnDisConnect    = SIGNAL('mqttOnDisconnect(QObject,QObject,QObject)')
    mqttOnMessage       = SIGNAL('mqttOnMessage(QObject,QObject,QObject)')
    mqttOnPublish       = SIGNAL('mqttOnPublish(QObject,QObject,QObject)')
    mqttOnSubscribe     = SIGNAL('mqttOnSubscribe(QObject,QObject,QObject,QObject)')
    mqttOnLog           = SIGNAL('mqttOnLog(QObject,QObject)')
    mqttOnTimeout       = SIGNAL('mqttOnTimeout(QObject)')
    
    mqttConnectionError = SIGNAL('mqttConnectionError(QObject,QObject)')

    # Hmmm new style signals cause problems with multiple parameters
#    mqttConnectionError =  QtCore.pyqtSignal([str]) 

# Add username/password
    def __init__(self,
                 creator,
                 clientId,
                 host = 'Mosquitto',
                 port = 1883,
                 poll = 2000,
                 keepAlive = 65534,
                 cleanSession = True):

        super(MQTTClient, self).__init__()
        # Load settings
        self._creator = creator

  # create client id
        self._cleanSession = cleanSession
        self._resetTimer = QTimer()    
        self._resetTimer.setSingleShot(True)
        self._resetTimer.timeout.connect( self._reset )

        self._killTimer = QTimer()    
        self._killTimer.setSingleShot(True)
        self._killTimer.timeout.connect( self._kill )
        self._killing = False

        self._loopTimer = QTimer()    
        self._loopTimer.setSingleShot(False)
        self._loopTimer.timeout.connect( self._loop )
        self._clientId = clientId
        self._host = host
        self._port = int(port)
        self._poll = int(poll)
        self.setKeepAlive(keepAlive)
        self._attempts = 0
        self._connected =False
        self._thread = QThread(self)
        self._thread.started.connect(lambda: self._loopTimer.start(self._poll))
        self._thread.finished.connect(self._loopTimer.stop)
        self._restarting = False
        self.mqttc = mosquitto.Mosquitto( self._clientId, self._cleanSession)
#        self.mqttc = paho.Client( self._clientId, self._cleanSession)
        
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.on_message = self.onMessage
        self.mqttc.on_publish = self.onPublish
        self.mqttc.on_subscribe = self.onSubscribe
        self.mqttc.on_log = self.onLog

    def run(self):
        Log.debug("MQTTClient Run")
        
        if self.isRunning() or self._killing:
            self.restart()
            return

        if self._restarting:
            self._thread.finished.disconnect(self.run)
            self._restarting =  False

        self._thread.start(QThread.LowestPriority)

    def stop(self):
      #  self._loopTimer.stop()
        self._thread.quit() # emits finished
        Log.debug("Thread stopped" + str(self.isRunning()))
        
    def isRunning(self):
        return self._thread.isRunning() 

    def _loop(self):
        self.loop()

        
    def setHost(self,host):
        self._host = host

    def setPort(self,port):
        self._port = int(port)

    def setPoll(self,poll):
        self._poll = int(poll)

    def setKeepAlive(self,keepAlive):
        self._keepAlive =  max(int(keepAlive) + int(self._poll),self.kMinKeepAlive)

    def getClientId(self):
        return self._clientId
    
    def on_connect(self,mosq, obj, rc):
        self._connected =True
        self._attempts = 0
        self.onConnect(mosq,obj,rc)
        
    def restart(self):
        if self.isRunning():
            self._restarting = True
            self._thread.finished.connect(self.run)
            if not self._killing:
                self.kill()
        else:
            self.run()



    def on_disconnect(self,mosq, obj, rc):
        Log.debug("disconnecting rc: "+str(rc) + " " + str(self._connected))
#        self._connected = False
        if self._killing:
            Log.debug("killing")
            self._kill()
        self.onDisConnect(mosq,obj,rc)
        self._attempts = 0
        self._connected = False

    def onConnect(self,mosq,obj,rc):
        QObject.emit(self,SIGNAL('mqttOnConnect'),self,obj,rc)
        pass

    def onDisConnect(self,mosq,obj,rc):
        QObject.emit(self,SIGNAL('mqttOnDisConnect'),self,obj,rc)
        pass
    

    def onMessage(self,mosq, obj, msg):
         QObject.emit(self,SIGNAL('mqttOnMessage'),self,obj,msg)
        # Log.debug('super ' + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    
    def onPublish(self,mosq, obj, mid):
        QObject.emit(self._creator,SIGNAL('mqttOnPublish'),self,obj,mid)
        Log.debug("mid: "+str(mid))
    
    def onSubscribe(self,mosq, obj, mid, granted_qos):
        QObject.emit(self,SIGNAL('mqttOnSubscribe'),self,obj,mid,granted_qos)
        Log.info("Subscribed: "+str(mid)+" "+str(granted_qos))
    
    def onLog(self,mosq, obj, level, string):
        QObject.emit(self,SIGNAL('mqttOnLog'),string,level)
        #Log.debug(string,level)

    def isConnected(self):
         return self.mqttc.socket() is not None and self._connected
    
    def publish(self,topic,msg,qos=0,retain=True):
        self.mqttc.publish(topic,msg,qos,retain)
    
    def subscribe(self,topic,qos):
        if self.isConnected():
            #Log.debug('Subscribing to ' + topic)
            self.mqttc.subscribe(topic,qos)

    def unsubscribe(self,topic):
        if self.isConnected():
           Log.debug('Unsubscribing to ' + topic)
           self.mqttc.unsubscribe(topic)
    
    def loop(self,timeout = 0.1):
        
        if (not self.isConnected()):
            if not self._killing:
                self._connect()
            return
    
        try:
            connResult = self.mqttc.loop(timeout)
            if connResult != mosquitto.MOSQ_ERR_SUCCESS:
                self._connected = False
                QObject.emit(self,SIGNAL('mqttConnectionError'),self,str(connResult))
        except ValueError as e:
                self._connected = False
                self._attempts=self._attempts+1
                if e == 'Invalid timeout.':
                    QObject.emit(self,SIGNAL('mqttOnTimeout'),self,"Connection Timeout")
                else:
                    Log.critical(str(e))
        except Exception as e:
                self._connected = False
                self._attempts=self._attempts+1
                QObject.emit(self,SIGNAL('mqttConnectionError'),self,str(e))
                Log.warn("Untrapped exception from loop " + str(e))
     
     
    def _kill(self):
        self._loopTimer.stop() # Stopped in self.stop but lets preempt this to avoid self.loop being called by running thread
        self._resetTimer.stop()
        self._killTimer.stop()
        self._killing = False
        self.stop()
        Log.debug("killed")
     
    def kill(self):
        try:
            if self.isConnected():
               self._disconnect()
            self._killing = True
            self._killTimer.start(self._keepAlive)
        except Exception as e:
            Log.warn("Error cleaning up " + str(e))
        pass
     
    def _connect(self):
        try:
           if self._connected == False:
               if not self._attempts < self.kMaxAttempts:
                    Log.warn("Max connection attempts reached.")
                    self._resetTimer.start(5000) # 1 minute parameterise
                    self.stop()
                    return
               Log.debug("Trying to connect")
               result =  self.mqttc.connect( self._host , self._port, self._keepAlive,1)
               self._connected = result ==  mosquitto.MOSQ_ERR_SUCCESS
               if not self._connected:
                    self._attempts = self._attempts +1
        except Exception as e:
            msg = 'MQTT Connection Error: ' + str(e)
            QObject.emit(self,SIGNAL('mqttConnectionError'),self,msg)
            Log.warn(msg)
            self._attempts = self._attempts +1
            self._connected = False


    def _disconnect(self):
        try:
            self.mqttc.disconnect()
        except Exception as e:
            Log.warn('MQTT Disconnection Error' + str(e))

    def _reset(self):
        self._attempts = 0
        self.start()
        Log.warn("Attempting to connect")

    

# Single shot client to get a single topic -> payload. Optionally perform a publish first

class tlMqttSingleShot(MQTTClient):

    mqttOnCompletion       = SIGNAL('mqttOnCompletion(QObject,QObject,QObject)')

    def __init__(self,
                 creator,
                 host,
                 port ,
                 pubTopic,
                 subTopic,
                 pubData = "",
                 timeout = 30, # seconds
                 qos = 1):

        self._creator   = creator
        self._pubTopic  = pubTopic
        self._subTopic  = subTopic
        self._pubData   = pubData
        self._qos       = int(qos)
        self._timeout   = timeout
        self._timer     = QTimer()         
        self._timer.setSingleShot(True)
        self._timer.timeout.connect( self._connectError )

        super(tlMqttSingleShot,self).__init__(self,
                                        str(self), 
                                        host,
                                        port,
                                        0,
                                        60,
                                        True)

        

    def _connectError(self,errormsg = "Timeout waiting for the broker"):
        Log.debug('Connection Timeout')
        QObject.emit(self,SIGNAL('mqttOnCompletion'),self,False,errormsg)
        self.kill()

    def run(self):
        self._timer.start(int(self._timeout) * 1000)
        QObject.connect(self, SIGNAL("mqttOnTimeout"), self._connectError)
        super(tlMqttSingleShot,self).run()
        
    def onDisConnect(self,mosq,obj,rc):
       super(tlMqttSingleShot,self).onDisConnect(mosq,obj,rc)
       self.kill()
       pass

    def kill(self):
        self._timer.stop()
        Log.debug(str(self) + " kill")
        super(tlMqttSingleShot,self).kill()
       

    def onConnect(self,mosq, obj, rc):
        if self._subTopic == None:
            self._connectError(False,"No Subcription Topic defined")
        self.subscribe(self._subTopic,self._qos)
        if self._pubTopic !=None:
           self.publish(self._pubTopic,self._pubData,self._qos)


    def onMessage(self,mq, obj, msg):
        Log.debug('onMessage!')
        QObject.emit(self,SIGNAL('mqttOnCompletion'),self,True,msg.payload)
        self.kill()

# Simple class for testing connections
# Add onComplete?

class tlMqttTest(MQTTClient):

    def __init__(self,
                 creator,
                 host,
                 port = 1883,
                 poll = 1):

        super(tlMqttTest,self).__init__(creator,
                                        str(self), # Add randown
                                        host,
                                        port,
                                        poll,
                                        60,
                                        True)
    
    
