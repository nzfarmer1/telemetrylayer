
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
import os, json

from TelemetryLayer.topicmanagers.agsense.ui_agtopicmanager import Ui_agTopicManager
from TelemetryLayer.topicmanagers.agsense.agtopicmanager import agTopicManager


    
class agTankTopicManager(agTopicManager):
    def __init__(self,iface=None):
        super(agTopicManager, self).__init__( False)
        pass

    def setEditorWidgetsV2(self,layer):
        fid = layer.dataProvider().fieldNameIndex("lowater")
        layer.setEditorWidgetV2(fid, 'Range')
        layer.setEditorWidgetV2Config(fid, {"Style": "Slider", "Min": 0,"Max":100,"Step":1})
        fid = layer.dataProvider().fieldNameIndex("height")
        layer.setEditorWidgetV2(fid, 'Range')
        layer.setEditorWidgetV2Config(fid, {"Style": "Slider", "Min": 1,"Max":5000,"Step":100})
 
    def setLayerStyle(self, layer):
        Log.debug("agTankTopicManager setLayerStyle " + os.path.join(self.path(), "rules.qml"))
        #_path = os.path.join(self.path(), "../")
       # if not _path in QgsApplication.svgPaths():
        #    QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [_path])
        self.loadStyle(layer, os.path.join(self.path(),  "rules.qml"))

    """
    getAttributes is no longer required for this manager.
    Alert status is stored in the JSON expression in the payload.
    Having a separate Alert attribute is just confusing. Similarly beforeCommit is no longer required.
    In summary, JSON encapsulated payloads are the way to go, but I will leave this code below as an
    example of adding a custom attribute on layer creation.
    
    """

    def setAttributes(self,layer,attrs): 
        fid = layer.dataProvider().fieldNameIndex("lowater")
        attrs.append(10) # start value of lowwater
        attrs.append(300) # start value of height
        return attrs

    def getAttributes(self): 
        attributes = [QgsField("lowater", QVariant.Int, "Alert", 1, 0, "Low water alert level (%)"),
                      QgsField("height", QVariant.Int, "Height", 1, 0, "Tank height (mm)")]
        return attributes

