# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlGenericTopicManager
 
 Support for Sys Topics

 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
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
def is_connected(values, feature, parent):
    return feature['connected']

@qgsfunction(0, u"Telemetry Layer")
def format_label(values, feature, parent):
    print "format_label\n"
    visible = int(feature.attribute('visible'))
    if visible == 0:
        return ""
    result =  str(feature.attribute('name')) + '\n(' + str(feature.attribute('payload')) + ')'
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
        palyr = QgsPalLayerSettings()
        palyr.readFromLayer(layer)
        palyr.enabled       = True 
        palyr.placement     = QgsPalLayerSettings.OverPoint
        palyr.quadOffset    = QgsPalLayerSettings.QuadrantBelow 
        palyr.yOffset       = 0.01
        palyr.fieldName     = '$format_label'
        palyr.writeToLayer(layer)
        if os.path.exists(os.path.join(self.path(),"ui_tleditfeature.ui")):
            Log.debug("setEditForm = " + os.path.join(self.path(),"ui_tleditfeature.ui"))
            layer.setEditForm(os.path.join(self.path(),"ui_tleditfeature.ui"))
            layer.setEditFormInit("editformfactory.featureDialog")
        layer.setEditorLayout(QgsVectorLayer.UiFileLayout)





    @staticmethod
    def register():
        pass

 
    @staticmethod
    def unregister():
        Log.debug("Un Registering Generic functions")
        if QgsExpression.isFunctionName("$is_connected"):
           QgsExpression.unregisterFunction("$is_connected")
        if QgsExpression.isFunctionName("$format_label"):
           QgsExpression.unregisterFunction("$format_label")
