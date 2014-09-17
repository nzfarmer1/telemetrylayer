# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlAbstractTopicManager
 
 Parent class for Topic Managers - not really Abstract
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject,QTimer
from PyQt4.QtGui  import QDialog, QTabWidget, QLabel, QDialogButtonBox, QPixmap,QLineEdit

from qgis.core import QgsPalLayerSettings,QgsVectorLayer
from qgis.utils import qgsfunction

import os
from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from tlxmltopicparser import tlXMLTopicParser as XMLTopicParser



class tlAbstractFeatureDialog(QObject):
    
    kOverviewTabId = 0
    kSettingsTabId = 1
    kHistoryTabId  = 2
    
    def __init__(self,dialog,tLayer,feature):
        self._dialog        = dialog
        self._tLayer        = tLayer
        self._layer         = tLayer.layer()
        self._feature       = feature
        self._widgets = {}

        self._qtimer = QTimer()    
#        self._qtimer.setSingleShot(False)
#        self._qtimer.timeout.connect( self._front )
#        self._qtimer.start(1000)

        Log.debug(dialog.editable())

        #for widget in dialog.children():
        #    for _widget in widget.children():
        #        if len(_widget.objectName()) >0:
        #            Log.debug(_widget.objectName())

#        for a in self._feature.fields().toList():
#            Log.debug(str(a.name()))
#            Log.debug(self._feature.attribute(a.name()))

        
    def show(self):
        # form is ready to be opened
        pass
    
    def _find(self,qtype,name):
        if name in self._widgets:
            return self._widgets[name]
        else:
            obj =  self._dialog.findChild(qtype,name)
            setattr(self,name,obj)
            self._widgets[name] = obj
            return obj
        
    """
    Keep dialog in front
    """
    def _front(self):
        if self._dialog !=None and self._dialog.isVisible():
            self._dialog.setWindowState(self._dialog.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self._dialog.activateWindow()
        else:
            self._qtimer.stop()

    def accept(self):
        Log.debug("Accept")
        self._dialog.save()



class tlSysFeatureDialog(tlAbstractFeatureDialog):
    
    def __init__(self,dialog,tLayer,feature):
        super(tlSysFeatureDialog,self).__init__(dialog,tLayer,feature)
        
    def show(self):
        Log.debug("Dialog Creating")
        tabWidget = self._find(QTabWidget,'tabWidget') # Remove History Tab!
        Log.debug(tabWidget)
        if tabWidget: # Always remove tabs from last to first
            tabWidget.removeTab(self.kHistoryTabId)
            tabWidget.removeTab(self.kSettingsTabId)
        image = self._find(QLabel,'imageWidget')
        pixmap = QPixmap(os.path.join(Settings.get('plugin_dir'),'icons','mqtticon-large.png'))
        image.setPixmap(pixmap)
#        name = self._find(QLineEdit,"name")
#        name.setEnabled(True)
        buttonBox = self._find(QDialogButtonBox,"buttonBox")
        buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        buttonBox.accepted.connect(lambda : tlSysFeatureDialog.validate(self))
        Log.debug(buttonBox)

    @staticmethod    
    def validate(self):
        Log.debug("Validating " + str(self._dialog))
        # Works but don't use
        if 0:
            Log.debug(self.name.text())
            name = self._find(self,"name")
            Log.debug(name.text())
            self._layer.startEditing()
            self._layer.changeAttributeValue ( self._feature.id(), 2, name.text())
            #self._dialog.changeAttribute("name",name.text())
            self._layer.commitChanges()
        super(tlSysFeatureDialog,self).accept() 




class tlAbstractTopicManager(QDialog,QObject):
    
    topicManagerReady       = QtCore.SIGNAL('topicManagerReady(QObject,QObject)')
    topicManagerError       = QtCore.SIGNAL('topicManagerError(QObject,QObject)')

    def __init__(self,broker,create=False):
       super(tlAbstractTopicManager, self).__init__()

       self._broker = broker
       self._create = create
       self._featureDialog = None
       
       systopicxml = os.path.join(Settings.get('plugin_dir'),'lib','systopics.xml')
       
       self._systopics = XMLTopicParser(systopicxml).getTopics()

    def featureDialog(self,dialog,tLayer,featureId):
         return tlSysFeatureDialog(dialog,tLayer,featureId)

    def setupUi(self):
       super(tlAbstractTopicManager,self).setupUi(self)

    def getTopics(self,topics = []):
        for topic in self._systopics:
           topics.append( topic )
        
        return topics
            
    def getWidget(self):
        pass

    def setFormatter(self,layer,topicType):
        palyr = QgsPalLayerSettings()
        palyr.readFromLayer(layer)
        palyr.enabled = True 
        palyr.placement= QgsPalLayerSettings.AroundPoint 
        palyr.fieldName = '$format_label'
        palyr.writeToLayer(layer)
        if os.path.exists(os.path.join(Settings.get('plugin_dir'),"featureforms","ui_tleditfeature.ui")):
            Log.debug("setEditForm = " + os.path.join(Settings.get('plugin_dir'),"featureforms","ui_tleditfeature.ui"))
            layer.setEditForm(os.path.join(Settings.get('plugin_dir'),"featureforms","ui_tleditfeature.ui"))
            layer.setEditFormInit("editformfactory.featureDialog")
        layer.setEditorLayout(QgsVectorLayer.UiFileLayout)

    def formatPayload(self,topicType,payload):
      return str(payload)
        
    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass
