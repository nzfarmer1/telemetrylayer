from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from TelemetryLayer.tltopicmanager import tlTopicManager
from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tlsettings import tlConstants as Constants
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tlmqttclient import *
import os

from TelemetryLayer.tlfeaturedock import  *


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

class tlRelayFeatureDock(tlFormFeatureDock):


    def __init__(self, iface, tlayer, feature):
        super(tlRelayFeatureDock,self).__init__(iface,tlayer,feature,False)
        self.topic = feature['topic']
        self.name.setText(feature['name'])
        self.relay = QtGui.QCheckBox(self.dockWidget)
        self.relay.setGeometry(QtCore.QRect(20, 150, 331, 111))
        self.relay.setObjectName(_fromUtf8("relay"))        
        self.relay.setText("Toggle")
        self.relay.stateChanged.connect(self.toggle)
        self.featureUpdated(self._tlayer,feature)
        self.dockWidget.show()

    def featureUpdated(self,tlayer,feat):
        try:
            Log.debug("Feature Updated")
            self.symbol.setPixmap(ActiveLayerSymbolPixmap(self._layer,feat))
            self.dockWidget.setWindowTitle(feat['match'])
            #Log.debug(self.relay.checkState())
            #Log.debug(feat['payload'])
            if str(self.relay.checkState()) !=  feat['payload']:
                self.relay.setChecked(feat['payload'] == "2")
        except Exception as e:
            Log.debug(str(e))
    
    def toggle(self,state):
        self._tlayer.publish(self.topic, str(state))
