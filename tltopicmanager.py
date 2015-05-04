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
from tlxmltopicparser import tlXMLTopicParser as XMLTopicParser




class tlTopicManager(QDialog, QObject):
    """
    Super class for all custom topic managers.
    
    Topic managers need to inherit from this class to provide the core list of topics
    and any additional configuration functions.
    
    Provides default handler's for defining a tLayer's settings (look and feel).
    
    """
    topicManagerReady = QtCore.SIGNAL('topicManagerReady(QObject,QObject)')
    topicManagerError = QtCore.SIGNAL('topicManagerError(QObject,QObject)')

    def __init__(self, broker, create=False):
        super(tlTopicManager, self).__init__()

        self._broker = broker
        self._create = create

        systopicxml = os.path.join(Settings.get('plugin_dir'), 'data', 'systopics.xml')

        self._systopics = XMLTopicParser(systopicxml).getTopics()

 
    def setupUi(self):
        super(tlTopicManager, self).setupUi(self)

    def getTopics(self, topics=[]):
        uniq = []
        _topics = []
        for topic in topics + self._systopics:
            if not topic['topic'] in uniq:
                _topics.append(topic)
                uniq.append(topic['topic'])

        return _topics

    def getWidget(self):
        pass

    def getAttributes(self, topicType =None):
        return []

    # Todo
    # Label not showing in Windows initially
    # Add symbols (rules based)

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
            palyr.yOffset = 0.01
            palyr.fieldName = '$format_label'
            palyr.writeToLayer(layer)
            Log.debug("Palyr Settings updated")
        except Exception as e:
            Log.debug("Error setting Label Format " + str(e))


    def instance(self,topicType):
        return self

    def beforeCommit(self,tLayer,values):
        pass

    def formatPayload(self, payload):
        return str(payload)

    def path(self, _class=None):
        if _class is None:
            module = sys.modules[self.__module__]
        else:
            module = sys.modules[_class.__module__]
        return os.path.dirname(module.__file__)


    def loadStyle(self, layer, filename):
        qfile = QFile(filename)
        if not qfile.open(QIODevice.ReadOnly):
            Log.debug("Unable to open file " + filename)
            return
        rules = qfile.readData(qfile.size())
        qfile.close()
        layer.loadNamedStyle(filename)
        #
 
