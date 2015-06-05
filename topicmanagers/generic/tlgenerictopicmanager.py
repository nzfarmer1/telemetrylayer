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

import os, imp

from qgis.utils import qgsfunction, QgsExpression
from qgis.core import *

from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tltopicmanager import tlTopicManager



class tlGenericTopicManager(tlTopicManager):
    def __init__(self,iface =None):
        super(tlGenericTopicManager, self).__init__( iface)
        self._topics = []

    def getWidget(self):
        super(tlGenericTopicManager, self).setupUi()
        QObject.emit(self, QtCore.SIGNAL('topicManagerReady'), True, self)
        return self.Tabs.widget(0)

 
    def setLayerStyle(self, layer):
        if not self.path() in QgsApplication.svgPaths():
            QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [self.path()])
        Log.debug("Loading QML " +os.path.join(self.path(), "rules.qml"))
        self.loadStyle(layer, os.path.join(self.path(), "rules.qml"))


    @staticmethod
    def register():

        path = os.path.join(os.path.dirname(__file__), 'qgsfuncs.py')
        if not QgsExpression.isFunctionName("$format_label"):
            imp.load_source('qgsfuncs', path)
        icons = os.path.join(os.path.dirname(__file__), 'icons')

        if not icons in QgsApplication.svgPaths():
            QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [icons])

        # from qgsfuncs import format_label
        pass


    @staticmethod
    def unregister():
        if QgsExpression.isFunctionName("$format_label"):
            QgsExpression.unregisterFunction("$format_label")
