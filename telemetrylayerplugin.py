# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Telemetry Layer
                                 A QGIS plugin
                             -------------------
        begin                : 2014-05-30
        copyright            : (C) 2014 by Andrew McClure
        email                : andrew@southweb.co.nz
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/


TODO

Global updates of all features where features <=> topic
Add History to DigiSense Topic Manager
Alternative host name selection
Username password for MQTT Broker
Stabilty and feature dialog for Windows and Linux


"""

from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *


import pdb 
# Initialize Qt resources from file resources.py
import os.path,sys, time, traceback
import webbrowser
import resources_rc
# Import the code for the dialog

from tlbrokers import tlBrokers as Brokers
from telemetrylayermanager import layerManager
from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from telemetrylayer import TelemetryLayer
from tltopicmanagerfactory import tlTopicManagerFactory as   TopicManagerFactory

import sys,os



class TelemetryLayerPlugin(QObject):

    def __init__(self, iface):
        # Save reference to the QGIS interface
        super(TelemetryLayerPlugin, self).__init__(iface)
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        sys.path.append(os.path.join(self.plugin_dir,"topicmanagers"))
        import editformfactory
        editformfactory.this = self
        
        self.layerManager = None
        self.installed = False
        self.configureDlg = None
        self.plugin_basename = str(os.path.basename(self.plugin_dir))

            
        # Initialise Settings and Log handlers
        try:
            Settings(self)
            Log(self)
            TopicManagerFactory(iface)
            Log.debug("Topic Managers Loaded")
            Brokers(os.path.join(self.plugin_dir,'data'))
        except Exception as e:
            Log.debug("Error on Plugin initialization " + str(e))
            
        Log.debug("Brokers Loaded")
        # initialize locale
        self.translator = QTranslator()
        
        if QSettings().value("locale/userLocale"):
            locale = QSettings().value("locale/userLocale")[0:2]
            localePath = os.path.join(self.plugin_dir, 'i18n', 'telemetrylayer_{}.qm'.format(locale))
            if os.path.exists(localePath):
                self.translator.load(localePath)

        if qVersion() > '4.3.3':
            QCoreApplication.installTranslator(self.translator)
            

        
    def initGui(self):
        # Tree Widget test
        Log.debug("initGUI")
        
        # Create action that will start plugin configuration
        self.aboutA = QAction(
            QIcon(":/plugins/"+ self.plugin_basename + "/icons/icon.png"),
            "About", self.iface.mainWindow()) # Replace or Add About
        # connect the action to the run method
        self.aboutA.triggered.connect(self.about)

        self.configureA = QAction(
            QIcon(":/plugins/"+ self.plugin_basename + "/icons/icon.png"),
            "Configure", self.iface.mainWindow()) # Replace or Add About
        # connect the action to the run method
        self.configureA.triggered.connect(self.configure)


        # From New Memory Layer plugin
        lMenuTitle = 'New Telemetry Layer...'

        self.newLayerA = QAction(
            QIcon(":/plugins/"+ self.plugin_basename + "/icons/icon.png"),
            lMenuTitle, self.iface.mainWindow())
        QObject.connect(self.newLayerA, SIGNAL("triggered()"), self.createLayer)
        self.iface.newLayerMenu().addAction(self.newLayerA)  # API >= 1.9
        self.iface.registerMainWindowAction(self.newLayerA, "Ctrl+F")

          
        try:
            self.layerManager   = layerManager(self )
            Log.debug("Layer Manager Loaded")
            self.telemetryLayer = TelemetryLayer(self) 
            Log.debug("Telemetry Layer Loaded")
            self.iface.projectRead.connect(self.layerManager.rebuildLegend)
            self.iface.newProjectCreated.connect(self.layerManager.rebuildLegend)
            Log.debug(Brokers.instance())
            Brokers.instance().brokersLoaded.connect(self.layerManager.brokersLoaded)
        except Exception as e:
            Log.critical(Settings.getMeta("name") + ": There was a problem loading the layer manager")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.debug(repr(traceback.format_exception(exc_type, exc_value,
                              exc_traceback)))

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.aboutA)
        self.iface.addToolBarIcon(self.configureA)
        self.iface.addPluginToMenu(u"&Telemetry Layer", self.aboutA)
        self.iface.addPluginToMenu(u"&Telemetry Layer", self.configureA)
        self.installed = True

        mw = self.iface.mainWindow()
#        lgd.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu);


    def unload(self):
        # Remove the plugin menu item and icon
        if not self.installed:
            return

        try:
            self.runTeardown()

            self.iface.removePluginMenu(u"&Telemetry Layer", self.aboutA)
            self.iface.removePluginMenu(u"&Telemetry Layer", self.configureA)
            self.iface.removeToolBarIcon(self.aboutA)
            self.iface.removeToolBarIcon(self.configureA)
            self.iface.newLayerMenu().removeAction(self.newLayerA)  # API >= 1.9
            self.iface.projectRead.disconnect(self.layerManager.rebuildLegend)
            self.iface.newProjectCreated.disconnect(self.layerManager.rebuildLegend)

            TopicManagerFactory.unregisterAll()
            Brokers.instance().brokersLoaded.disconnect(self.layerManager.brokersLoaded)
        except:
            TopicManagerFactory.unregisterAll()
            pass
        finally:
            Log.debug("Plugin unloaded")
            
        
        

    def runTeardown(self):
        try:
            self.layerManager.tearDown()
            self.telemetryLayer.tearDown()
            
        except Exception as e:
            Log.debug(e)
            pass
    
    def about(self):
        
       webbrowser.open(Settings.getMeta("homepage"))
#        for broker in Brokers.instance().list():
#            Log.debug(broker.topicManager())
#        return
        

    def configure(self):
        self.telemetryLayer.instance().show()

    
    def createLayer(self):
        if self.layerManager != None:
            self.layerManager.createEmptyLayer()

    def freshInstall(self):
        version = Settings.get('version')
        current = Settings.getMeta('version')
        return current != version
           
           
