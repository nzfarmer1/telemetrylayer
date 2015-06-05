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

from TelemetryLayer.topicmanagers.agsense.agtopicmanager import agTopicManager

    
class agRelayTopicManager(agTopicManager):
    def __init__(self,iface=None):
        super(agTopicManager, self).__init__(iface)
        pass


    def setLayerStyle(self, layer):
        Log.debug("agTopicManager setLayerStyle " + os.path.join(self.path(), "../",  "agsense.qml"))
        _path = os.path.join(self.path(), "../")
       # if not _path in QgsApplication.svgPaths():
        #    QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [_path])
        self.loadStyle(layer, os.path.join(_path,  "agsense.qml"))




