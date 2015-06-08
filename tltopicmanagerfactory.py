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
from tltopicmanager import tlTopicManager as TopicManager

import traceback, sys, time,os,imp,pkgutil,glob,types


@qgsfunction(0, u"Telemetry Layer")
def is_connected(values, feature, parent):
    try:
        return  int(feature['connected']) == 1 or feature['connected'] == 'true' or feature['connected'] == 'True'
    except (KeyError,TypeError):
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
    except (KeyError, TypeError):
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



def get_subpackages(module):
    dir = os.path.dirname(module.__file__)

    def is_package(d):
        d = os.path.join(dir, d)
        return os.path.isdir(d) and glob.glob(os.path.join(d, '__init__.py*'))

    return filter(is_package, os.listdir(os.path.dirname(module.__file__)))


def get_modules(module):
    dir = os.path.dirname(module.__file__)

    def is_module(d):
        d = os.path.join(dir, d)
        return '.pyc' in os.path.splitext(d) and not ('__init__' in d or 'ui_' in d or 'qgsfuncs' in d)

    return filter(is_module, os.listdir(os.path.dirname(module.__file__)))


# Adapted from recipe adapted from http://stackoverflow.com/users/1736389/sam-p


def registerLocal():
    _tms = []
    package = topicmanagers
    for package in get_subpackages(topicmanagers):
        path = os.path.join(os.path.dirname(topicmanagers.__file__), package)
        if path not in sys.path:
            sys.path.append(path)
        module = __import__(package)
        meta = module.classFactory()
        for m in meta:
            m['id'] = m['name'].replace(" ","_").lower()
            Log.debug("Loading topic manager " + str(m['class']))
            _tms.append(m)
    return _tms



class tlTopicManagerFactory():
    """
    Factory class to keep register and keep track of all custom topic managers
    
    """
    registered = []
    topicManagers = []


    @staticmethod
    def featureUpdated(layer, feature):
        pass

    @staticmethod
    def registerAll():

        tlTopicManagerFactory.topicManagers = registerLocal()

        for tmeta in tlTopicManagerFactory.topicManagers:
           tlTopicManagerFactory.registerTopicManager(tmeta)

    @staticmethod
    def unregisterAll():
        print "topicmanagerfactory unregisterAll"
        for _id in tlTopicManagerFactory.getTopicManagerIds():
            tlTopicManagerFactory.unregisterTopicManager(_id)
        tlTopicManagerFactory.unregister()

    @staticmethod
    def registerTopicManager(tmeta):
        if not tmeta['id'] in tlTopicManagerFactory.registered:
            _obj = tlTopicManagerFactory.getTopicManagerById(tmeta['id'])
            if hasattr(_obj, "register"):
                _obj.register()
                _obj.setId(tmeta['id'])
                _obj.setName(tmeta['name'])
            tlTopicManagerFactory.registered.append(tmeta['id'])

    @staticmethod
    def unregisterTopicManager(_id):
        if _id in tlTopicManagerFactory.registered:
            _obj = tlTopicManagerFactory.getTopicManagerById(_id)
            if hasattr(_obj, "unregister"):
                _obj.unregister()
            del _obj    
            tlTopicManagerFactory.registered.remove(_id)


    @staticmethod
    def getTopicManagerList():
        return tlTopicManagerFactory.topicManagers

    @staticmethod   
    def getTopicManagers():
        objs = []
        for tm in tlTopicManagerFactory.topicManagers:
            objs.append(tm['class'])
        return objs

    @staticmethod
    def getTopicManagerIds():
        ids = []
        for tm in tlTopicManagerFactory.getTopicManagerList():
            ids.append(tm['id'])
        return ids


    @staticmethod
    def getTopicManagerById(_id):
        _obj = None
        for topicManager in tlTopicManagerFactory.getTopicManagerList():
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

_tmf = tlTopicManagerFactory #shortcut
