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
    def __init__(self):
        super(tlGenericTopicManager, self).__init__( )
        self._topics = []

 
    def setLayerStyle(self, layer):
        if not self.path(tlGenericTopicManager) in QgsApplication.svgPaths():
            QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [self.path(tlGenericTopicManager)])
        Log.debug("Loading QML " +os.path.join(self.path(tlGenericTopicManager), "rules.qml"))
        rules = os.path.join(self.path(tlGenericTopicManager), "rules.qml")
        self.loadStyle(layer, rules)


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
