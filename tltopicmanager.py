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
import TelemetryLayer
from tlxmltopicparser import tlXMLTopicParser as XMLTopicParser



class tlFeatureDialog(QObject):
    
    kOverviewTabId = 0
    kSettingsTabId = 1
    kHistoryTabId  = 2
        
    def __init__(self,dialog,tLayer,feature,Tabs =None, tabsList = []):
        self._dialog        = dialog
        self._tLayer        = tLayer
        self._layer         = tLayer.layer()
        self._feature       = feature
        self._editable      = dialog.editable()
        self._widgets = {}
        
        if Tabs != None:
            for idx in tabsList:
                title = Tabs.tabText(idx)
                self._addTab(Tabs.widget(idx),title)

        
        super(tlFeatureDialog,self).__init__()
        Log.debug("Dialog Editable " + str(dialog.editable()))
        
        
        self._dialog.adjustSize()
        self.topicManager = self._tLayer.topicManager()
        self.topicType = self._tLayer.topicType()
        self.updated = self._find(QLabel,'updatedValue')
        self.updated.setStyleSheet("font-weight:bold;")
        self.changed = self._find(QLabel,'changedValue')
        self.changed.setStyleSheet("font-weight:bold;")
        self.payload = self._find(QLabel,'payloadValue')
        self.payload.setStyleSheet("font-weight:bold;")

        buttonBox = self._find(QDialogButtonBox,"buttonBox")
        buttonBox.accepted.connect(lambda : tlFeatureDialog._validate(self))
        
        buttonBox.clicked.connect(lambda : tlFeatureDialog._clicked(self))

        self._tLayer.featureUpdated.connect(self._update)
        self.update()
        
    def _update(self,tLayer,feature):
        if feature.id() == self._feature.id():
            self._feature = feature
            self.update()

    @staticmethod    
    def _clicked(self,btn = None):
        Log.debug(btn)
        self.clicked()
        pass


    @staticmethod
    def _validate(self):
        self.validate()

    def _addTab(self,widget,title):
        tabWidget = self._find(QTabWidget,'tabWidget') # Remove History Tab!
        Log.debug("add Tab " + str(widget))
        tabWidget.addTab(widget,title)
        pass
        
    def update(self): # check if current tab!
        try:
            if hasattr(self.updated,"setText"):
                updated = self._feature['updated']
                self.updated.setText(self._since(int (updated)))
            if hasattr(self.changed,"setText") :
                changed = self._feature['changed']
                self.changed.setText(self._since(int(changed)))
            if hasattr(self.payload,"setText") :
                payload = self.topicManager.formatPayload(self.topicType,self._feature['payload'])
                self.payload.setText(payload)
        except Exception as e:
            Log.debug(str(e))
            pass

        
    def validate(self):
        self.accept() 

    def clicked(self):
        self.accept() 

    
    def show(self):
        # form is ready to be opened
        pass
        
    @staticmethod
    def _since(when,fmt = True):
        if not int(when)>=0:
            return ""
        
        # replace with datetime methods!
        
        hDiv = 0.00027777777778
        mDiv = 0.01666666666667
        
        delta = time.time() - when
        if not fmt:
            return delta
        hours  = int(delta * hDiv)
        mins   = int((delta - (hours *3600)) * mDiv)
        secs   = int((delta - (hours *3600) - (mins*60)))        
        fmtStr = ""
        if hours > 0:
            fmtStr = fmtStr + str(hours) + 'h '
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
        Log.debug("_del " +str(self))
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
       
 
    def validate(self):
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

    def setLabelFormatter(self,layer,topicType):
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

    def setFeatureForm(self,layer,topicType):
        _form  = os.path.join(TelemetryLayer.path(),"topicmanagers","ui_tleditfeature.ui")
        if os.path.isfile(_form):
            Log.debug("setEditForm = " + _form)
            layer.setEditForm(_form)
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
 
