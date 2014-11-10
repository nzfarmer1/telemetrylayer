"""

tlBrokers

Store, retrieve, list and find Brokers. Broker get and set params
"""

from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from PyQt4.QtCore import QFile, QIODevice, QObject, pyqtSignal
from PyQt4.QtGui import QFileDialog
import json, os.path, sys


class BrokerNotFound(Exception):
    pass


class BrokerNotSynced(Exception):
    pass


class BrokersNotDefined(Exception):
    pass


class tlBrokers(QObject):
    """
    Class to manage array of Brokers including storage
    
    """

    _this = None
    brokersLoaded = pyqtSignal(object)

    kDefaultFile = "brokers.json.default"

    @staticmethod
    def instance():
        return tlBrokers._this

    def __init__(self, pluginDir):
        super(tlBrokers, self).__init__()
        self._jsonfile = None
        self._loaded = False
        self._dirty = False
        self._brokers = []
        self._oldBrokers = None
        self._dirty = False
        self._dirtyList = []
        self._defaultFile = os.path.join(pluginDir, self.kDefaultFile)
        self._jsonfile = Settings.get("brokerFile", self._defaultFile)
        tlBrokers._this = self
        self.load()

    def load(self):
        try:
            if os.path.exists(self._jsonfile):
                qfile = QFile(self._jsonfile)
                qfile.open(QIODevice.ReadOnly)
                jsonstr = qfile.readData(qfile.size())
                qfile.close()
                self._brokers = json.loads(jsonstr)
                self._validate()
                self.brokersLoaded.emit(self._dirtyList)
                self._dirtyList[:] = []
                self._dirty = False
            else:
                Log.critical("Broker file " + self._jsonfile + " not found!")
        except Exception as e:
            Log.critical(e)

        self._dirty = False
        pass

    def _file(self):
        if self._jsonfile == self._defaultFile:
            fileName = QFileDialog.getSaveFileName(None, "Location for Brokers File",  # translate
                                                   "~/",
                                                   "*.json")
            if fileName:
                Settings.set('brokerFile', fileName)
                self._jsonfile = fileName
            else:
                Log.critical("Broker data being saved to plugin directory and will be lost on upgrade!")

        return self._jsonfile

    def sync(self, load=True):
        if not self._dirty:
            return
        try:
            qfile = QFile(self._file())
            qfile.open(QIODevice.WriteOnly)
            qfile.writeData(json.dumps(self._brokers))
            qfile.flush()
            qfile.close()
            self._dirty = False
            if load:
                self.load()
        except Exception as e:
            Log.critical(e)

    def uniq(self):
        if len(self._brokers) == 0:
            return 1
        return int(max(self._brokers.keys(), key=int)) + 1

    def uniqName(self, bid, name):
        uniq = True
        for broker in self.list():
            if bid != broker.id() and broker.name() == name:
                uniq = False
                break
        return uniq


    def list(self, reverse=False):
        brokers = []
        if len(self._brokers) == 0:
            return []
        for bid, brokerprops in self._brokers.iteritems():
            brokers.append(tlBroker(bid, brokerprops))
        if reverse:
            brokers.reverse()
        return brokers

    def find(self, bid):
        try:
            return tlBroker(bid, self._brokers[bid])
        except:
            return None

    def findByName(self, name):
        broker = None
        try:
            for _broker in self.list():
                if name == _broker.name():
                    broker = _broker
            return broker
        except:
            return None

    def create(self, name=None, host="localhost", port=1883):
        broker = tlBroker(self.uniq())
        if name is None:
            broker.setName("Broker" + str(broker.id()))
        broker.setHost(host)
        broker.setPort(port)
        broker.setPoll(0)
        broker.setKeepAlive(0)
        self._brokers[broker.id()] = broker.properties()
        self._dirty = True
        return broker

    def update(self, broker):
        self._brokers[broker.id()] = broker.properties()
        self._dirty = True
        self._dirtyList.append(broker.id())
        pass

    def delete(self, broker):
        del self._brokers[broker.id()]
        self._dirty = True
        pass


    def _validate(self):
        pass

    def dirty(self):
        return self._dirty


class tlBroker(QObject):
    """
    Class to represent a single Broker
    
    """

    def __init__(self, brokerId, properties={}):
        self._properties = properties
        self.setId(brokerId)
        super(tlBroker, self).__init__()
        pass

    def properties(self):
        return self._properties


    def id(self):
        return self.get("id")

    def set(self, key, value):
        self._properties[key] = value

    def get(self, key, default=None):
        if key in self._properties:
            return self._properties[key]
        return default

    def setId(self, id):
        self.set('id', id)

    def setName(self, name):
        self.set('name', name)

    def setHost(self, host):
        self.set('host', host)

    def setKeepAlive(self, keepalive):
        self.set('keepalive', keepalive)

    def setPort(self, port):
        self.set('port', port)

    def setPoll(self, poll):
        self.set('poll', poll)

    def setTopics(self, topics):
        self.set('topics', topics)
        Log.debug("tlBroker set Topics")

    def setTopicManager(self, topicManager):
        self.set('topicManager', topicManager)

    # return individual topic
    def topic(self, topic):
        topics = self.topics(None, topic)
        if len(topics) > 0:
            return topics[0]
        else:
            return None

    def topics(self, type_=None, topic_=None):
        topics = self.get('topics')
        if type_ is None and topic_ is None:
            return topics
        _topics = []
        for topic in topics:
            if type_ is None or topic['type'] == type_:
                if topic_ is None or topic_ == topic['topic']:
                    _topics.append(topic)

        return _topics

    def topicManager(self):
        return self.get('topicManager')

    def name(self):
        return self.get('name')

    def host(self):
        return self.get('host')

    def poll(self, poll=0):
        if self.get('poll') is None:
            return poll
        return self.get('poll')

    def port(self):
        return self.get('port')

    def keepAlive(self):
        return self.get('keepalive')

    def uniqTopicTypes(self):
        types = []
        for topic in self.topics():
            if not topic['type'] in types:
                types.append(topic['type'])
        return types
