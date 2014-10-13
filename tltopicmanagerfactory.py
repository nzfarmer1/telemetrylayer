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


import topicmanagers
from lib.tllogging import tlLogging as Log
from tltopicmanager import tlTopicManager as TopicManager, tlFeatureDialog  as DialogManager

import traceback,sys

class tlTopicManagerFactory():
    
    registered = []
    featureDialogs = []
    
    topicManagers  = []

    @staticmethod
    def featureUpdated(layer,feature):
        pass

    @staticmethod
    def registerAll():
        
        Log.debug("Loading Topic Managers")
        tlTopicManagerFactory.topicManagers =  topicmanagers.register()
  
        for _id in tlTopicManagerFactory.getTopicManagerIds():
            tlTopicManagerFactory.registerTopicManager(_id)
            
    @staticmethod
    def unregisterAll():
        print "topicmanagerfactory unregisterAll"
        for _id in tlTopicManagerFactory.getTopicManagerIds():
            tlTopicManagerFactory.unregisterTopicManager(_id)

    @staticmethod
    def registerTopicManager(_id):
        if not _id in tlTopicManagerFactory.registered:
            _obj  = tlTopicManagerFactory.getTopicManagerById(_id)
            if hasattr(_obj,"register"):
                _obj.register()
            tlTopicManagerFactory.registered.append(_id)
            
    @staticmethod
    def unregisterTopicManager(_id):
        if _id in tlTopicManagerFactory.registered:
            _obj  = tlTopicManagerFactory.getTopicManagerById(_id)
            if hasattr(_obj,"unregister"):
                _obj.unregister()
            del(_obj)
            tlTopicManagerFactory.registered.remove(_id)

    @staticmethod
    def getTopicManager(broker,create = False):
        try:
            _class = tlTopicManagerFactory.getTopicManagerById(broker.topicManager())
            if not _class:
                Log.alert("Error loading topic manager " + str(broker.id()))
            return _class(broker,create)
        except Exception as e:
            Log.debug("Unable to load topic manager from " + str(broker.topicManager()) + " " + str(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.debug(repr(traceback.format_exception(exc_type, exc_value,
                                      exc_traceback)))

            return None
 
    @staticmethod
    def getTopicManagers():
        return tlTopicManagerFactory.topicManagers

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
                    _obj =  topicManager['class']
                except Exception as e:
                    Log.debug(str(e))
                break
        return _obj
        
    def __init__(self,iface):
        self.registerAll()
