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
import collections

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


def get_modules(module,ext):
    dir = os.path.dirname(module.__file__)

    def is_module(d):
        d = os.path.join(dir, d)
        return ext in os.path.splitext(d) and d != module.__file__ and not ('__init__' in d or 'ui_' in d or 'qgsfuncs' in d)

    return filter(is_module, os.listdir(os.path.dirname(module.__file__)))


def reload_class(class_obj):
    module_name = class_obj.__module__
    module = sys.modules[module_name]
    Log.debug("Reloading module " + module_name)
    for module_pycfile in get_modules(module,'.pyc'):
        Log.debug("reloading " + module_pycfile)
        os.remove(os.path.join(os.path.dirname(module.__file__), module_pycfile))
        # pycfile = module.__file__
        pycfile = module_pycfile
        Log.debug("Reloading " + pycfile)
        modulepath = pycfile.replace(".pyc", ".py")
        _module_name = modulepath.replace(".py", "")
        Log.debug("importing " + os.path.join(os.path.dirname(module.__file__), modulepath))
        code = open(os.path.join(os.path.dirname(module.__file__), modulepath), 'rU').read()
        compile(code, _module_name, "exec")
        _module = sys.modules[_module_name]
        _module = reload(_module)
    for module_pyfile in get_modules(module,'.py'):
        Log.debug("xprocessing " + module_pyfile)
        modulepath = module_pyfile
        _module_name = modulepath.replace(".py", "")
        Log.debug("ximporting " + os.path.join(os.path.dirname(module.__file__), modulepath))
        code = open(os.path.join(os.path.dirname(module.__file__), modulepath), 'rU').read()
        compile(code, _module_name, "exec")
        _module = sys.modules[_module_name]
        del _module
        import module   
        _module = reload(_module)
    return getattr(module, class_obj.__name__)

def import_class(_class):
    from importlib import import_module
    mod = import_module(_class.__module__)
    try:
        reload_class(_class)
        #reload(sys.modules[_class.__module__])
    except KeyError:
      #  Log.debug("Failed to reload class " + str(_class))
        pass
    klass = getattr(mod, _class.__name__)
    return klass()


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
            _tMF.register(m)


class tlTopicManagerFactory():
    """
    Factory class to keep register and keep track of all custom topic managers
    
    """
    topicManagers = {}


    @staticmethod
    def registerAll():
        registerLocal()


    @staticmethod
    def tearDown():
        try:
            print "topicmanagerfactory tearDown"
            for item in _tMF.list():
                _tMF.unregister(item.id)
            _tMF.unregisterFuncs()
        except Exceptions as e:
            Log.debug("Error tearing down Topic Managers: " + str(e))

    @staticmethod
    def register(meta):
        """
        register a topic manager of the form {name:name,class:class} where class is a module.class string
        add to internal dict of topic managers
        defer actual loading until class is loaded via load method
        """
        if not (meta.has_key('name')  and meta.has_key('class')):
            Log.debug("Telemetry Layer: Attempting to register a topic manager with out name or class")
            return

        if _tMF._findByClass(meta['class']):
            Log.debug(meta['name'] + " already registered")
            return

        if hasattr(meta['class'],"register"):
            meta['class'].register() # register itself
        
        meta['id'] = meta['name'].replace(" ","_").lower()
        Log.debug("Loading topic manager " + str(meta['class']))
        _tMF.topicManagers[meta['id']] = meta

    @staticmethod
    def unregister(_id):
        meta = _tMF._findById(_id)
        if meta.has_key('obj'):
            _obj = meta['obj']
            if hasattr(_obj, "unregister"):
                _obj.unregister()
            del _obj    
        del _tMF.topicManagers[_id]

    @staticmethod
    def _findById(_id):
        return _tMF.topicManagers[_id]

    @staticmethod
    def _findByClass(_class):
        return filter(lambda x: _class  == x['class'], _tMF.topicManagers.itervalues())


    @staticmethod
    # return id and name (not class and obj)
    def list():
        metas = []
        TopicManager = collections.namedtuple('TopicManager','name id')
        map(lambda x: metas.append(TopicManager(id=x['id'],name=x['name'])),
                    _tMF.topicManagers.itervalues())
        return reversed(metas)


    @staticmethod
    def load(_id):
        tm = _tMF._findById(_id)
        if not tm:
            return None # throw Topic Manager Not Found!
        if not tm.has_key('obj'):
            tm['obj'] = import_class(tm['class'])
            tm['obj'].setName(tm['name'])
            tm['obj'].setId(tm['id'])
            _tMF.topicManagers[_id] = tm
        return tm['obj']


    def __init__(self, iface):
        self.registerAll()


    @staticmethod
    def unregisterFuncs():
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

_tMF = tlTopicManagerFactory #shortcut
