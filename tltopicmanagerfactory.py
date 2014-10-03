# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlTopicManagerFactory
 
 Factory class to return instances of the correct topic manager
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject
from PyQt4.QtGui  import QDialog


from tlabstracttopicmanager import tlAbstractTopicManager as TopicManager, tlAbstractFeatureDialog  as DialogManager
from tlfiletopicmanager import tlFileTopicManager
from tlgenerictopicmanager import tlGenericTopicManager
from dstopicmanager import dsTopicManager
from lib.tllogging import tlLogging as Log



class tlTopicManagerFactory():
    
    registered = []
    featureDialogs = []
    
    @staticmethod
    def featureUpdated(layer,feature):
        pass
    #    dlg = DialogManager.findDialog(layer,feature)
    #    if dlg !=None:
    #        dlg.update(feature)
            
    @staticmethod
    def registerAll():
        for _id in tlTopicManagerFactory.getTopicManagerIds():
            tlTopicManagerFactory.registerTopicManager(_id)
            
    @staticmethod
    def unregisterAll():
        for _id in tlTopicManagerFactory.getTopicManagerIds():
            tlTopicManagerFactory.unregisterTopicManager(_id)

    @staticmethod
    def registerTopicManager(_id):
        if not _id in tlTopicManagerFactory.registered:
            _obj  = tlTopicManagerFactory.getTopicManagerById(_id)
            _obj.register()
            tlTopicManagerFactory.registered.append(_id)
            
    @staticmethod
    def unregisterTopicManager(_id):
        if _id in tlTopicManagerFactory.registered:
            _obj  = tlTopicManagerFactory.getTopicManagerById(_id)
            _obj.unregister()
            tlTopicManagerFactory.registered.remove(_id)

    @staticmethod
    def getTopicManager(broker,create = False):
        try:
            _class = tlTopicManagerFactory.getTopicManagerById(broker.topicManager())
            if not _class:
                Log.alert("Error loading topic manager " + str(broker.id()))
                return None
            return _class(broker,create)
        except:
            Log.debug("Unable to load topic manager from " + str(broker.topicManager()))
            return None
 
    @staticmethod
    def getTopicManagers():
        return [{'id':'digisense','name':"DigiSense",'class':"dsTopicManager"},
                {'id':'file','name':"Topic File (XML)",'class':"tlFileTopicManager"},
                {'id':'generic','name':"Generic MQTT",'class':"tlGenericTopicManager"}]

    @staticmethod
    def getTopicManagerIds():
        ids = []
        for tm in tlTopicManagerFactory.getTopicManagers():
            ids.append(tm['id'])
        return ids


    @staticmethod
    def getTopicManagerById(_id):
        _obj = None
        for topicManager in tlTopicManagerFactory.getTopicManagers():
            if topicManager['id'] == _id:
                try:
                    _obj =  eval(topicManager['class'])
                except Exception as e:
                    Log.debug(str(e))
                break
        return _obj
        
