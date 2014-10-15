# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlTopicManager
 
 Parent class for Topic Managers - sub class this to create your own dialog
 ***************************************************************************/
"""
import sip
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject,QTimer,QFile,QIODevice,QTextStream
from PyQt4.QtGui  import QDialog, QTabWidget, QLabel, QDialogButtonBox, QPixmap,QLineEdit
from PyQt4.QtXml import QDomDocument,QDomNode,QDomElement


from qgis.core import QgsPalLayerSettings,QgsVectorLayer,QgsFeatureRequest
from qgis.utils import qgsfunction,QgsExpression

import os,sys,math,time
from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from tlxmltopicparser import tlXMLTopicParser as XMLTopicParser



class tlFeatureDialog(QObject):
    
    kOverviewTabId = 0
    kSettingsTabId = 1
    kHistoryTabId  = 2
    
    
    def __init__(self,dialog,tLayer,feature):
        self._dialog        = dialog
        self._tLayer        = tLayer
        self._layer         = tLayer.layer()
        self._feature       = feature
        self._editable      = dialog.editable()
        self._widgets = {}
        super(tlFeatureDialog,self).__init__()
        
        Log.debug("Dialog Editable " + str(dialog.editable()))
        self._tLayer.featureUpdated.connect(self._update)
        self._dialog.adjustSize()
        self.topicManager = self._tLayer.topicManager()
        self.topicType = self._tLayer.topicType()


    def _update(self,tLayer,feature):
        if feature.id() == self._feature.id():
            self._feature = feature
            self.update()
    
    def update(self):
        pass
    
    def show(self):
        # form is ready to be opened
        pass
    
    def _since(self,when,fmt = True):
        if not int(when)>=0:
            return ""
        
        delta = time.time() - when
        if not fmt:
            return delta
        hours = int(delta / 3600)
        mins = int((delta - hours) % 60)
        secs  = int((delta - hours) % 60)
        
        fmtStr = ""
        if hours > 0:
            fmtStr = fmtStr + str(hours) + 'h'
        fmtStr = fmtStr + str(mins) + 'm '  
        fmtStr = fmtStr + str(secs) + 's ago'  
        
        return fmtStr

    
    def _find(self,qtype,name):
        if name in self._widgets:
            return self._widgets[name]
        else:
            obj =  self._dialog.findChild(qtype,name)
            setattr(self,name,obj)
            self._widgets[name] = obj
            return obj
        

    def accept(self):
        Log.debug("Accept")
        self._dialog.save()

    def __del__(self):
        self._tLayer.featureUpdated.disconnect(self._update)
        if self._editable:
            self._tLayer.featureDialogClosed.emit(self._tLayer)
        pass
        



class tlSysFeatureDialog(tlFeatureDialog):
    
    def __init__(self,dialog,tLayer,feature):
        super(tlSysFeatureDialog,self).__init__(dialog,tLayer,feature)

        
    def show(self):
        Log.debug("Dialog Creating")
        tabWidget = self._find(QTabWidget,'tabWidget') # Remove History Tab!
        if tabWidget: # Always remove tabs from last to first
            tabWidget.removeTab(self.kHistoryTabId)
            tabWidget.removeTab(self.kSettingsTabId)
        image = self._find(QLabel,'imageWidget')
        pixmap = QPixmap(os.path.join(Settings.get('plugin_dir'),'icons','mqtticon-large.png'))
        image.setPixmap(pixmap)
#        name = self._find(QLineEdit,"name")
#        name.setEnabled(True)
       
        buttonBox = self._find(QDialogButtonBox,"buttonBox")
        buttonBox.accepted.connect(lambda : tlSysFeatureDialog.validate(self))
        
        buttonBox.clicked.connect(lambda : tlSysFeatureDialog.clicked(self))

        updated = self._find(QLabel,'updatedValue')
        updated.setStyleSheet("font-weight:bold;")
        changed = self._find(QLabel,'changedValue')
        changed.setStyleSheet("font-weight:bold;")
        payload = self._find(QLabel,'payloadValue')
        payload.setStyleSheet("font-weight:bold;")
        self.update()
        
    def update(self):
        updated = self._find(QLabel,'updatedValue')
        updated.setText(self._since(int (self._feature['updated'])))
        changed = self._find(QLabel,'changedValue')
        changed.setText(self._since(int(self._feature['changed'])))
        payload = self._find(QLabel,'payloadValue')
        payload.setText(self.topicManager.formatPayload(self.topicType,self._feature['payload']))
        
    @staticmethod    
    def clicked(self,btn = None):
        Log.debug(btn)
        pass

 
    @staticmethod
    def validate(self):
        # editmode doesn't work properly from the GUI
        # See: https://hub.qgis.org/issues/11395
        # the following code works but don't use
        if False:
            Log.debug(self.name.text())
            name = self._find(self,"name")
            Log.debug(name.text())
            self._layer.startEditing()
            self._layer.changeAttributeValue ( self._feature.id(), 2, name.text())
            #self._dialog.changeAttribute("name",name.text())
            self._layer.commitChanges()
        super(tlSysFeatureDialog,self).accept() 




class tlTopicManager(QDialog,QObject):
    
    topicManagerReady       = QtCore.SIGNAL('topicManagerReady(QObject,QObject)')
    topicManagerError       = QtCore.SIGNAL('topicManagerError(QObject,QObject)')

    def __init__(self,broker,create=False):
       super(tlTopicManager, self).__init__()

       self._broker = broker
       self._create = create
       self._featureDialog = None
       
       systopicxml = os.path.join(Settings.get('plugin_dir'),'data','systopics.xml')
       
       self._systopics = XMLTopicParser(systopicxml).getTopics()

    def featureDialog(self,dialog,tLayer,featureId): # Check SYS type?
         return tlSysFeatureDialog(dialog,tLayer,featureId)

    def setupUi(self):
       super(tlTopicManager,self).setupUi(self)

    def getTopics(self,topics = []):
        uniq    = []
        _topics = []
        for topic in topics + self._systopics:
           if not topic['topic'] in uniq:
                _topics.append(topic)
                uniq.append(topic['topic'])

        return _topics
            
    def getWidget(self):
        pass

    def getAttributes(self,layer,topicType):
        return []

# Todo
# Label not showing in Windows initially
# Add symbols (rules based)

    def setFormatter(self,layer,topicType):
        palyr = QgsPalLayerSettings()
        palyr.readFromLayer(layer)
        palyr.enabled = True 
        palyr.placement= QgsPalLayerSettings.AroundPoint 
        palyr.fieldName = '$format_label'
        palyr.writeToLayer(layer)
        Log.debug("Setting feature form to:" + os.path.join(self.path(),"topicmanagers","ui_tleditfeature.ui"))
              
        layer.setEditForm(os.path.join(Settings.get('plugin_dir'),"topicmanagers","ui_tleditfeature.ui"))
        layer.setEditFormInit("editformfactory.featureDialog")
        layer.setEditorLayout(QgsVectorLayer.UiFileLayout)

    def formatPayload(self,topicType,payload):
      return str(payload)

    def path(self,_class  =None):
        if _class == None:
            module = sys.modules[self.__module__]
        else:
            module = sys.modules[_class.__module__]
        return os.path.dirname(module.__file__)
        
        
    def loadStyle(self,layer,filename):
        qfile = QFile(filename)
        if not qfile.open(QIODevice.ReadOnly):
            Log.debug("Unable to open file " + filename)
            return
        rules = qfile.readData(qfile.size())
        qfile.close()
        layer.loadNamedStyle(filename)
        #
 
