# -*- coding: utf-8 -*-
"""
/***************************************************************************
 agTopicManager
 
 DigiSense Topic Manager - needs backend DigiSense server. 

 ***************************************************************************/
Todo:
Save device type parameters as attributes
Use these to create traffic lights on icon or set alerts

- In agTopicManager Update alert attribute to True of ! Appended
- Use MQTT Logo as default symbol
- Increment in lambda to scale x as [1..1024] for percentage functions

"""

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

import os, imp


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


class agTopicManager(tlTopicManager):
    """
    Implementation of tlTopicManager
    """

    def __init__(self):
        super(agTopicManager, self).__init__()


    def setLabelFormatter(self, layer): # remove topicType
        try:
            palyr = QgsPalLayerSettings()
            palyr.readFromLayer(layer)
            palyr.enabled = True
            palyr.fontBold = True
            palyr.shapeDraw = True
            palyr.shapeTransparency = 0
            palyr.shapeType = QgsPalLayerSettings.ShapeRectangle
            palyr.textColor = QColor(255,255,255) # white
            palyr.placement = QgsPalLayerSettings.OverPoint
            palyr.quadOffset = QgsPalLayerSettings.QuadrantBelow
            palyr.multilineAlign = QgsPalLayerSettings.MultiCenter
            palyr.yOffset = 2
            palyr.labelOffsetInMapUnits = False
            palyr.fieldName =  '$agsense_format_label'
            palyr.writeToLayer(layer)
            Log.debug("Palyr Settings updated")
        except Exception as e:
            Log.debug("Error setting Label Format " + str(e))

    def setLayerStyle(self, layer):
        Log.debug("agTopicManager setLayerStyle " + self.path() + "/agsense.qml")
        self.loadStyle(layer, os.path.join(self.path(), "agsense.qml"))


    @staticmethod
    def register():

        if  not QgsExpression.isFunctionName("$agsense_format_label"): # check to make sure these are not already registered
            path = os.path.join(os.path.dirname(__file__), 'qgsfuncs.py')
            imp.load_source('qgsfuncs', path)
      
        icons = os.path.join(os.path.dirname(__file__), 'icons')

        if not icons in QgsApplication.svgPaths():
            QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [icons])

    

    @staticmethod
    def unregister():
        if QgsExpression.isFunctionName("$agsense_format_label"):
            QgsExpression.unregisterFunction("$agsense_format_label")

        if QgsExpression.isFunctionName("$agsense_alert"):
            QgsExpression.unregisterFunction("$agsense_alert")


