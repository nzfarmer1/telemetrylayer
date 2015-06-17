# -*- coding: utf-8 -*-
"""

Plugin Folder Name: TelemetryLayerSamplePlugin

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSlot, SIGNAL, SLOT
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import QgsMapToolEmitPoint

from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tltopicmanagerfactory import tlTopicManagerFactory as   TopicManagerFactory
from TelemetryLayer.tlfeaturedock import tlTextFeatureDock as TextFeatureDock
from TelemetryLayer.topicmanagers.generic.tlgenerictopicmanager import tlGenericTopicManager as ParentTopicManager

import sys, os, imp


class MyFeatureDock(TextFeatureDock):

    def __init__(self, iface, tlayer, feature,show = True):
        super(MyFeatureDock,self).__init__(iface,tlayer,feature,show)


    def featureUpdated(self,tlayer,feat):
        try:
            # do what you need here.  Draw it yourself if required!
            super(MyFeatureDock,self).featureUpdated(tlayer,feat)
            Log.debug("MyFeatureDock - featureUpdated: " + str(feat['payload']))
            layer = tlayer.layer()
            fieldId = layer.dataProvider().fieldNameIndex("context")
            layer.startEditing()
            layer.changeAttributeValue(feat.id(), fieldId, "fubar")
            layer.commitChanges()

        except Exception as e:
            Log.debug("Error on MyFeatureDock - featureUpdated: " + str(e))
        pass


class sampleTopicManager(ParentTopicManager):
    """
     Sub class of tlTopicManager
    """

    def __init__(self):
        super(sampleTopicManager, self).__init__()
    
    def getFeatureDock(self,iface,tlayer,feature):
        return MyFeatureDock(iface,tlayer,feature)

    def setPalLabelSettings(self,palyr):
        palyr.fieldName =  '$sample_format_label'

#    def setLayerStyle(self, layer):
#        if os.path.exists(os.path.join(self.path(), "sample.qml")):
#            self.loadStyle(layer, os.path.join(self.path(), "sample.qml"))


    @staticmethod
    def register():
        if  not QgsExpression.isFunctionName("$sample_format_label"): # check to make sure these are not already registered
            path = os.path.join(os.path.dirname(__file__), 'qgsfuncs.py')
            Log.debug(path)
            imp.load_source('qgsfuncs', path)

    @staticmethod
    def unregister():
        if QgsExpression.isFunctionName("$sample_format_label"):
            QgsExpression.unregisterFunction("$sample_format_label")



class TelemetryLayerSampleTopicManager(QObject):
    """
    Plugin Class - providing hook into QGIS core; starting point for setup and teardown;
    including creation of menu/icon actions.
    
    Todo: Alternative host name selection
    Username password for MQTT Broker
    """

    def __init__(self, iface):
        super(TelemetryLayerSampleTopicManager, self).__init__(iface)
        self.iface = iface
   
    def initGui(self):
        # Tree Widget test
        Log.debug("Sample Plugin init")

        self.iface.newProjectCreated.connect(
            lambda: TopicManagerFactory.register({'name':"Sample TM",'class':sampleTopicManager})
            # Add more as required
            )

        QgsProject.instance().readProject.connect(
            lambda: TopicManagerFactory.register({'name':"Sample TM",'class':sampleTopicManager})
            # Add more as required
            )
        
        
    def unload(self):
        pass
