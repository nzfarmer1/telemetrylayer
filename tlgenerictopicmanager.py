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

from qgis.utils import qgsfunction,QgsExpression
from qgis.core import *
import os

from tltopicmanager import tlTopicManager,tlFeatureDialog
from ui_tlgenerictopicmanager import Ui_tlGenericTopicManager 
from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
 

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



    @qgsfunction(0, u"Telemetry Layer")
    def is_connected(values, feature, parent):
        return feature.attribute('connected')

    @qgsfunction(0, u"Telemetry Layer")
    def format_label(values, feature, parent):
        result = str(feature.attribute('name')) + '\n(' + str(feature.attribute('payload')) + ')'
        return result

    @staticmethod
    def register():
        Log.debug("Registering Generic functions")

    @staticmethod
    def unregister():
        Log.debug("Un Registering Generic functions")
                # Unregister functions
        QgsExpression.unregisterFunction("is_connected")
        QgsExpression.unregisterFunction("format_label")
