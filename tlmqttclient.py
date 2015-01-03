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

#from lib import mosquitto
from lib import client as mqtt
import sys
import traceback
import socket
from socket import error as socket_error
from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from tlbrokers import tlBroker as Broker

# TODO
# Add eExceptions for 32 Broke Pipe and 54 Connection Reset by Peer

class MQTTClient(QtCore.QObject):
    """
    Wrapper class for Mosquitto MQTT client
    Provides inherited helper classes for SingleShot and Test requests
    Initial approach was to sub class QThread, but reading revealed that
    running the timers within a thread was the preferred approach.
    
    
    """

    kMaxAttempts    = 3
    kMinKeepAlive   = 5
    kResetTimer     = 60

    mqttOnConnect = SIGNAL('mqttOnConnect(QObject,QObject,QObject)')
    mqttOnDisConnect = SIGNAL('mqttOnDisconnect(QObject,QObject,QObject)')
    mqttOnMessage = SIGNAL('mqttOnMessage(QObject,QObject,QObject)')
    mqttOnPublish = SIGNAL('mqttOnPublish(QObject,QObject,QObject)')
    mqttOnSubscribe = SIGNAL('mqttOnSubscribe(QObject,QObject,QObject,QObject)')
    mqttOnLog = SIGNAL('mqttOnLog(QObject,QObject)')
    mqttOnTimeout = SIGNAL('mqttOnTimeout(QObject)')

    mqttConnectionError = SIGNAL('mqttConnectionError(QObject,QObject)')

    # Hmmm new style signals cause problems with multiple parameters
    #    mqttConnectionError =  QtCore.pyqtSignal([str])

    # Add username/password
    def __init__(self,
                 creator,
                 clientId,
                 broker,
                 cleanSession=True):

        super(MQTTClient, self).__init__()
        # Load settings
        self._creator = creator

        # create client id
        self._cleanSession = cleanSession
        self._resetTimer = QTimer()
        self._resetTimer.setSingleShot(True)
        self._resetTimer.timeout.connect(self._reset)

        self._killTimer = QTimer()
        self._killTimer.setSingleShot(True)
        self._killTimer.timeout.connect(self._kill)
        self._killing = False

        self._loopTimer = QTimer()
        self._loopTimer.setSingleShot(False)
        self._loopTimer.timeout.connect(self._loop)
        self._clientId = clientId
        self._host = broker.host()
        self._port = int(broker.port())
        self._poll = int(broker.poll())
        self.setKeepAlive(broker.keepAlive())
        self._attempts = 0
        self._connected = False
        self._thread = QThread(self)
        self._thread.started.connect(lambda: self._loopTimer.start(self._poll))
        self._thread.finished.connect(self._loopTimer.stop)

        self._thread.started.connect(lambda:Log.debug("Thread started"))
        self._thread.finished.connect(lambda:Log.debug("Thread stopped"))
        self._thread.terminated.connect(lambda:Log.debug("Thread terminated"))
        self._restarting = False
        self.mqttc = mqtt.Client(self._clientId, self._cleanSession)
        #        self.mqttc = paho.Client( self._clientId, self._cleanSession)

        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.on_message = self.onMessage
        self.mqttc.on_publish = self.onPublish
        self.mqttc.on_subscribe = self.onSubscribe
        self.mqttc.on_log = self.onLog

    def run(self):
        Log.debug("MQTT client run")

        if self.isRunning() or self._killing:
            self.restart()
            return

        if self._restarting:
            self._thread.finished.disconnect(self.run)
            self._restarting = False

        self._thread.start(QThread.LowestPriority)

    def stop(self):
        self._thread.quit()  # emits finished
        Log.debug("Thread quit")

    def isRunning(self):
        return self._thread.isRunning()

    def _loop(self):
        self.loop()

    def setHost(self, host):
        self._host = host

    def host(self):
        return self._host

    def setPort(self, port):
        self._port = int(port)

    def port(self):
        return self._port

    def setPoll(self, poll):
        self._poll = int(poll)

    def setKeepAlive(self, keepAlive):
        self._keepAlive = max(int(keepAlive) + int(self._poll), self.kMinKeepAlive)

    def getClientId(self):
        return self._clientId

    def on_connect(self, mqtt, obj,flags, rc):
        self._connected = True
        self._attempts = 0
        self.onConnect(mqtt, obj, rc)

    def restart(self):
        Log.debug("Restarting")
        if self.isRunning():
            self._restarting = True
            self._thread.finished.connect(self.run)
            if not self._killing:
                self.kill()
        else:
            self.run()


    def on_disconnect(self, mqtt, obj, rc):
        Log.debug("disconnecting rc: " + str(rc) + " " + str(self._connected))
        #        self._connected = False
        if self._killing:
            Log.debug("killing")
            self._kill()
        self.onDisConnect(mqtt, obj, rc)
        self._attempts = 0
        self._connected = False

    def onConnect(self, mqtt, obj, rc):
        QObject.emit(self, SIGNAL('mqttOnConnect'), self, obj, rc)
        pass

    def onDisConnect(self, mqtt, obj, rc):
        QObject.emit(self, SIGNAL('mqttOnDisConnect'), self, obj, rc)
        pass


    def onMessage(self, mqtt, obj, msg):
        QObject.emit(self, SIGNAL('mqttOnMessage'), self, obj, msg)
        # Log.debug('super ' + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

    def onPublish(self, mqtt, obj, mid):
        QObject.emit(self._creator, SIGNAL('mqttOnPublish'), self, obj, mid)
        Log.debug("mid: " + str(mid))

    def onSubscribe(self, mqtt, obj, mid, granted_qos):
        QObject.emit(self, SIGNAL('mqttOnSubscribe'), self, obj, mid, granted_qos)
        Log.info("Subscribed: " + str(mid) + " " + str(granted_qos))

    def onLog(self, mqtt, obj, level, string):
        QObject.emit(self, SIGNAL('mqttOnLog'), string, level)
        #Log.debug(string,level)

    def isConnected(self):
        return self.mqttc.socket() is not None and self._connected

    def publish(self, topic, msg, qos=0, retain=True):
        self.mqttc.publish(str(topic), msg, int(qos), retain)   

    def subscribe(self, topic, qos):
        if self.isConnected():
            try:
                Log.debug('Subscribing to ' + topic + " " + str(qos))
                self.mqttc.subscribe(str(topic), int(qos))
                Log.debug('Subscribed to ' + topic + " " + str(qos))
            except Exception as e:
                Log.debug("Error on subscribe " + str(e))
                raise e

    def unsubscribe(self, topic):
        if self.isConnected():
            Log.debug('Unsubscribing to ' + topic)
            self.mqttc.unsubscribe(topic)

    def loop(self, timeout=0.1):

        if not self.isConnected():
            if not self._killing:
                self._connect()
            return
        try:
            connResult = self.mqttc.loop(timeout)
            if connResult != mqtt.MQTT_ERR_SUCCESS:
                self._connected = False
                QObject.emit(self, SIGNAL('mqttConnectionError'), self, str(connResult))
        except ValueError as e:
            self._connected = False
            self._attempts += 1
            if e == 'Invalid timeout.':
                QObject.emit(self, SIGNAL('mqttOnTimeout'), self, "Connection Timeout")
            else:
                Log.critical(str(e))
        except Exception as e:
            self._connected = False
            self._attempts += 1
            QObject.emit(self, SIGNAL('mqttConnectionError'), self, str(e))
            Log.warn("Untrapped exception from loop " + str(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.debug(repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback)))


    def _kill(self):
        self._loopTimer.stop()  # Stopped in self.stop but lets preempt this to avoid self.loop being called by running thread
        self._killTimer.stop()
        self._killing = False
        self._reset() # reset timer
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
            if not self._connected:
                if not self._attempts < self.kMaxAttempts:
                    if not self._resetTimer.isActive():
                        Log.warn("Max connection attempts reached - waiting " + str(self.kResetTimer) + " seconds" )
                        self._resetTimer.start(self.kResetTimer*1000)  # 1 minute parameterise
                    #self.stop()
                    return
                Log.debug("Trying to connect")
                result = self.mqttc.connect(str(self._host), int(self._port),int( self._keepAlive), 1)
                self._connected = result == mqtt.MQTT_ERR_SUCCESS
                if not self._connected:
                    self._attempts += 1
        except Exception as e:
            msg = 'MQTT Connection Error: ' + str(e) + ' ' + self._host + ":" + str(self._port)

            QObject.emit(self, SIGNAL('mqttConnectionError'), self, msg)
            Log.warn(msg)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.debug(repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback)))
            self._attempts += 1
            self._connected = False


    def _disconnect(self):
        try:
            self.mqttc.disconnect()
        except Exception as e:
            Log.warn('MQTT Disconnection Error' + str(e))

    def _reset(self):
        Log.warn("Timer reset ")
        self._attempts = 0
        self._resetTimer.stop() # not required
        #self.run()


# Single shot client to get a single topic -> payload. Optionally perform a publish first

class tlMqttSingleShot(MQTTClient):
    mqttOnCompletion = SIGNAL('mqttOnCompletion(QObject,QObject,QObject)')

    def __init__(self,
                 creator,
                 broker,
                 pubTopic,
                 subTopics=[],
                 pubData="",
                 qos=0,
                 callback = None,
                 callbackonerr  =None):

        self._creator = creator
        self._pubTopic = pubTopic
        self._subTopics = subTopics
        self._pubData = pubData
        self._broker = broker.clone()
        self._qos = int(qos)
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._connectError)
        self._callback = None
        self._callbackonerr = None

        self._broker.setPoll(1)
        self._broker.keepAlive(10)

        if 'method' in str(type(callback)):
            self._callback = callback
            
        if 'method' in str(type(callbackonerr)):
            self._callbackonerr = callbackonerr
        
        super(tlMqttSingleShot, self).__init__(self,
                                               str(self),
                                               broker)  # keep alive


    def _connectError(self, errormsg="Timeout waiting for the broker"):
        Log.debug('Connection Timeout')
        QObject.emit(self, SIGNAL('mqttOnCompletion'), self, False, errormsg)
        if not self._callbackonerr is None:
            self._callbackonerr(self,False,msg)
        elif not self._callback is None:
            self._callback(self,False,msg)
        self.kill()

    def run(self):
        self._timer.start(int(self._broker.keepAlive()) * 1000)
        QObject.connect(self, SIGNAL("mqttOnTimeout"), self._connectError)
        super(tlMqttSingleShot, self).run()

    def onDisConnect(self, mqtt, obj, rc):
        super(tlMqttSingleShot, self).onDisConnect(mqtt, obj, rc)
        self.kill()
        pass

    def loop(self):
        #        Log.debug("Looping " + str(self._poll))
        super(tlMqttSingleShot, self).loop()

    def kill(self):
        self._timer.stop()
        super(tlMqttSingleShot, self).kill()


    def onConnect(self, mqtt, obj, rc):
        if len(self._subTopics) == 0:
            self._connectError(False, "No Subcription Topic defined")
        for topic in self._subTopics:
            self.subscribe(str(topic), self._qos)
        if self._pubTopic is not None:
            self.publish(str(self._pubTopic), str(self._pubData), self._qos)


    def onMessage(self, mq, obj, msg):
        Log.debug('onMessage!')
        self._timer.stop()
        mq.disconnect()
        QObject.emit(self, SIGNAL('mqttOnCompletion'), self, True, msg)
        if not self._callback is None:
            self._callback(self,True,msg)


# Simple class for testing connections
# Add onComplete?

class tlMqttTest(MQTTClient):
    def __init__(self,
                 broker):
        _broker = broker.clone()
        _broker.setPoll(1)
        _broker.keepAlive(10)

        super(tlMqttTest, self).__init__(self,
                                         str(_broker),
                                         h_broker)
    
    
