# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlTopicManager
 
 Parent class for Topic Managers - sub class this to create your own dialog
 ***************************************************************************/
"""
import sip
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, QTimer, QFile, QIODevice, QTextStream
from PyQt4.QtGui import QDialog, QTabWidget, QLabel, QDialogButtonBox, QPixmap, QLineEdit, QColor
from PyQt4.QtXml import QDomDocument, QDomNode, QDomElement

from qgis.core import QgsPalLayerSettings, QgsVectorLayer, QgsFeatureRequest
from qgis.utils import qgsfunction, QgsExpression

import os, sys, math, time
from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
import TelemetryLayer

from tlfeaturedock import tlTextFeatureDock as FeatureDock


class tlTopicManager(QObject):
    """
    Super class for all custom topic managers.
    
    Topic managers need to inherit from this class to provide the core list of topics
    and any additional configuration functions.
    
    Provides default handler's for defining a tLayer's settings (look and feel).
    
    """

    def __init__(self):
        super(tlTopicManager, self).__init__()

    def getFeatureDock(self,iface,tlayer,feature):
        return FeatureDock(iface,tlayer,feature)


    def getAttributes(self):
        return []

    def setAttributes(self,layer,attrs):
        return attrs

    def setEditorWidgetsV2(self, layer): # add custom formatters
        Log.debug("Default setEditorWidgetsV2")
        pass


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
            self.setPalLabelSettings(palyr) # obj so pass by reference
            palyr.writeToLayer(layer)
            Log.debug("Palyr Settings updated")
        except Exception as e:
            Log.debug("Error setting Label Format " + str(e))


    def onMessage(self,tlayer,msg):
       """
       Pre process any messages prior to feature['payload'] being updated
       msg.payload is passed as reference and can be modified 
       Return False if the data is not to be committed to the feature
       Example Use case: save image data to file and replace payload with filename
       
       """
       return True


    def path(self, _class=None):
        if _class is None:
            module = sys.modules[self.__module__]
        else:
            module = sys.modules[_class.__module__]
        return os.path.dirname(module.__file__)

    def setPalLabelSettings(self,palyr):
        palyr.fieldName = '$format_label'

    def loadStyle(self, layer, filename):
        qfile = QFile(filename)
        if not qfile.open(QIODevice.ReadOnly):
            Log.debug("Unable to open file " + filename)
            return
        rules = qfile.readData(qfile.size())
        qfile.close()
        layer.loadNamedStyle(filename)

    def id(self):
        return self._id
    
    def name(self):
        return self._name

    def setId(self,_id):
        self._id = _id

    def setName(self,name):
        self._name = name
