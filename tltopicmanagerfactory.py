# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlTopicManagerFactory
 
 Factory class to return instances of the correct topic manager
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject
from PyQt4.QtGui import QDialog

from qgis.utils import qgsfunction, QgsExpression
import topicmanagers
from lib.tllogging import tlLogging as Log
from lib.tlsettings import tlSettings as Settings

from tltopicmanager import tlTopicManager as TopicManager, tlFeatureDialog  as DialogManager

import traceback, sys, time


@qgsfunction(0, u"Telemetry Layer")
def is_connected(values, feature, parent):
    try:
        return int(feature['connected']) == 1 or feature['connected'] == 'true' or feature['connected'] == 'True'
    except KeyError:
        return 0


@qgsfunction(0, u"Telemetry Layer")
def is_visible(values, feature, parent):
    result = True
    try:
        result = int(feature['visible']) == 1
    except TypeError:
        result = feature['visible'] == 'true' or feature['visible'] == 'True'
    except KeyError:
        result = False
    finally:
        return result


@qgsfunction(0, u"Telemetry Layer")
def is_changed(values, feature, parent):
    result = 0
    try:
        result = (int(time.time()) - int(feature['changed'])) < int(Settings.get('changedTimeout', 25))
    except KeyError, TypeError:
        return 0
    finally:
        return result


@qgsfunction(0, u"Telemetry Layer")
def since_change(values, feature, parent):
    result = 0
    try:
        result = (int(time.time()) - int(feature['changed']))
    except KeyError:
        return 0
    finally:
        return result


@qgsfunction(0, u"Telemetry Layer")
def is_silent(values, feature, parent):
    try:
        return (int(time.time()) - int(feature['updated'])) >= int(Settings.get('updatedTimeout', 15))
    except KeyError:
        return 0


class tlTopicManagerFactory():
    """
    Factory class to keep register and keep track of all custom topic managers
    
    """

    registered = []
    featureDialogs = []
    topicManagers = []
    classObjects = {}

    @staticmethod
    def featureUpdated(layer, feature):
        pass

    @staticmethod
    def registerAll():

        Log.debug("Loading Topic Managers")
        tlTopicManagerFactory.topicManagers = topicmanagers.register()

        for _id in tlTopicManagerFactory.getTopicManagerIds():
           tlTopicManagerFactory.registerTopicManager(_id)

    @staticmethod
    def unregisterAll():
        print "topicmanagerfactory unregisterAll"
        for _id in tlTopicManagerFactory.getTopicManagerIds():
            tlTopicManagerFactory.unregisterTopicManager(_id)
        tlTopicManagerFactory.unregister()

    @staticmethod
    def registerTopicManager(_id):
        if not _id in tlTopicManagerFactory.registered:
            _obj = tlTopicManagerFactory.getTopicManagerById(_id)
            if hasattr(_obj, "register"):
                _obj.register()
            tlTopicManagerFactory.registered.append(_id)

    @staticmethod
    def unregisterTopicManager(_id):
        if _id in tlTopicManagerFactory.registered:
            _obj = tlTopicManagerFactory.getTopicManagerById(_id)
            if hasattr(_obj, "unregister"):
                _obj.unregister()
            del _obj
            tlTopicManagerFactory.registered.remove(_id)

    @staticmethod
    def getTopicManager(broker, create=False):
        Log.debug("Get topic manager "+ str(broker))
        try:
            if not create and broker.id() in tlTopicManagerFactory.classObjects:
                return tlTopicManagerFactory.classObjects[broker.id()]

            _class = tlTopicManagerFactory.getTopicManagerById(broker.topicManager())
            if not _class:
                Log.alert("Error loading topic manager " + str(broker.id()))
                return None

            tlTopicManagerFactory.classObjects[broker.id()] = _class(broker, create)
            return tlTopicManagerFactory.classObjects[broker.id()]
        except Exception as e:
            Log.progress("Unable to load topic manager from " + str(broker.topicManager()) + " " + str(e))
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
                    _obj = topicManager['class']
                except Exception as e:
                    Log.debug(str(e))
                break
        return _obj

    def __init__(self, iface):
        self.registerAll()

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        Log.debug("Un Registering Generic functions")
        if QgsExpression.isFunctionName("$is_connected"):
            QgsExpression.unregisterFunction("$is_connected")

        if QgsExpression.isFunctionName("$is_visible"):
            QgsExpression.unregisterFunction("$is_visible")

        if QgsExpression.isFunctionName("$is_changed"):
            QgsExpression.unregisterFunction("$is_changed")

        if QgsExpression.isFunctionName("$since_change"):
            QgsExpression.unregisterFunction("$since_change")

        if QgsExpression.isFunctionName("$is_silent"):
            QgsExpression.unregisterFunction("$is_silent")
