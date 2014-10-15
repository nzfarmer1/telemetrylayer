# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlGenericTopicManager
 
 Support for Sys Topics

 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui, QtXml
from PyQt4.QtCore import *
from PyQt4.QtGui import *


import os

from qgis.utils import qgsfunction,QgsExpression
from qgis.core import *

from TelemetryLayer.tltopicmanager import tlTopicManager,tlFeatureDialog
from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tllogging import tlLogging as Log

from ui_tlgenerictopicmanager import Ui_tlGenericTopicManager
 

@qgsfunction(0, u"Telemetry Layer")
def format_label(values, feature, parent):
    result = "No data"
    try:
        visible = int(feature.attribute('visible'))
        if visible == 0:
            result = ""
        else:
            result =  str(feature.attribute('name')) + '\n(' + str(feature.attribute('payload')) + ')'
    except:
        pass
    finally:
        return result

class tlGenericTopicManager(tlTopicManager, Ui_tlGenericTopicManager):
    
    def __init__(self,broker,create=False):
        super(tlGenericTopicManager,self).__init__(broker,create)
        self._topics = []
        self._broker = broker
        self._create = create
        self._featureDialog =None


    def featureDialog(self,dialog,tLayer,feature):
        try:
            # Let the $SYS type in the super class handle this 
            return  super(tlGenericTopicManager,self).featureDialog(dialog,tLayer,feature)
        except Exception as e:
            Log("featureDialog " + str(e))
            return None


    def getWidget(self):
        super(tlGenericTopicManager,self).setupUi()
        QObject.emit(self,QtCore.SIGNAL('topicManagerReady'),True,self)
        return self.Tabs.widget(0)

    def setFormatter(self,layer,topicType):
        Log.debug("setFormatter")
        palyr = QgsPalLayerSettings()
        palyr.readFromLayer(layer)
        palyr.enabled       = True 
        palyr.placement     = QgsPalLayerSettings.OverPoint
        palyr.quadOffset    = QgsPalLayerSettings.QuadrantBelow 
        palyr.yOffset       = 0.01
        palyr.fieldName     = '$format_label'
        palyr.writeToLayer(layer)

        if not self.path() in QgsApplication.svgPaths():
            QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [self.path()])
        self.loadStyle(layer,os.path.join(self.path(),"rules.qml"))
        
        if os.path.exists(os.path.join(self.path(),"ui_tleditfeature.ui")):
            Log.debug("setEditForm = " + os.path.join(self.path(),"ui_tleditfeature.ui"))
            layer.setEditForm(os.path.join(self.path(),"ui_tleditfeature.ui"))
            layer.setEditFormInit("editformfactory.featureDialog")
        layer.setEditorLayout(QgsVectorLayer.UiFileLayout)
        #Log.debug("Setting svg paths")
        #Log.debug(QgsApplication.svgPaths())
        


    @staticmethod
    def register():
        pass

 
    @staticmethod
    def unregister():
        if QgsExpression.isFunctionName("$format_label"):
           QgsExpression.unregisterFunction("$format_label")
