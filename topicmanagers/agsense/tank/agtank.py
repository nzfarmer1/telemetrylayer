
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

from TelemetryLayer.topicmanagers.agsense.agtopicmanager import agTopicManager
from TelemetryLayer.tlfeaturedock import  *


    
class tlTankFeatureDock(tlSVGFeatureDock):


    def __init__(self, iface, tlayer, feature):

        super(tlTankFeatureDock,self).__init__(iface,tlayer,feature,False)
        svg = QByteArray()
        svg.append('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="300px" height="300px" viewBox="0 0 300 300" enable-background="new 0 0 300 300" xml:space="preserve"><g><rect x="0" y="0" rx="10" ry="10" width="300" height="300" fill="#001E26"></rect></g><g><path fill="none" stroke="#004153" stroke-width="10" stroke-linecap="round" stroke-miterlimit="10" d="M101.79092927350956,207.45333323392336a75,75 0 1,1 96.4181414529809,-7.105427357601002e-15"></path></g><g id="Amount"><path fill="none" stroke="#00C8FF" stroke-width="10" stroke-linecap="round" stroke-miterlimit="10" d="M101.79092927350956,207.45333323392336a75,75 0 0,1 35.18545740147067,-131.31391470983897"></path></g><g id="Mark"> <path fill="#FFFFFF" d="M132.00391565249078,72.05039481718119L136.97638667498023,76.1394185240844L140.25045252758815,70.59630786869424L132.00391565249078,72.05039481718119z"></path></g><g><text transform="matrix(1 0 0 1 150 150)" text-anchor="middle" fill="#00C8FF" font-family="Roboto" font-size="30">200</text></g><g><path fill="#FFFFFF" d="M120,167l-3.8,2.42v-4.83L120,167z"></path></g><g><text transform="matrix(1 0 0 1 150 170)" text-anchor="middle" fill="#FFFFFF" font-family="Roboto" font-size="11">200 U/min</text></g><g><text transform="matrix(1 0 0 1 150 45)" text-anchor="middle" fill="#00C8FF" font-family="Roboto" font-size="11">Engine</text></g></svg>')
        self.svgWidget.load(svg)
        self.featureUpdated(self._tlayer,feature)
        self.dockWidget.show()

    def featureUpdated(self,tlayer,feat):
        try:
            Log.debug("Feature Updated")
            self.dockWidget.setWindowTitle(feat['match'])
            #Log.debug(self.relay.checkState())
            #Log.debug(feat['payload'])
        except Exception as e:
            Log.debug(str(e))
    
    def toggle(self,state):
        self._tlayer.publish(self.topic, str(state))
        

class agTankTopicManager(agTopicManager):
    def __init__(self):
        super(agTankTopicManager, self).__init__( )
        pass

    def getFeatureDock(self,iface,tlayer,feature):
        return tlTankFeatureDock(iface,tlayer,feature)

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


    def setAttributes(self,layer,attrs): 
        fid = layer.dataProvider().fieldNameIndex("lowater")
        attrs.append(10) # start value of lowwater
        attrs.append(300) # start value of height
        return attrs

    def getAttributes(self): 
        attributes = [QgsField("lowater", QVariant.Int, "Alert", 1, 0, "Low water alert level (%)"),
                      QgsField("height", QVariant.Int, "Height", 1, 0, "Tank height (mm)")]
        return attributes

