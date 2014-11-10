"""
Dynamically load/reload topic manager packages
"""

import pkgutil
import os
import sys
import glob
import imp
from TelemetryLayer.lib.tllogging import tlLogging as Log
import TelemetryLayer.topicmanagers

# Recipe from http://stackoverflow.com/users/66713/james-emerton

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


# Recipe adapted from http://stackoverflow.com/users/1736389/sam-p

def reload_classx(class_obj):
    module_name = class_obj.__module__
    module = sys.modules[module_name]
    Log.debug("Reloading modules")
    for modile_pycfile in get_modules(module):
        os.remove(os.path.join(os.path.dirname(module.__file__), modile_pycfile))
    pycfile = module.__file__
    modulepath = pycfile.replace(".pyc", ".py")
    code = open(modulepath, 'rU').read()
    compile(code, module_name, "exec")
    module = reload(module)
    return getattr(module, class_obj.__name__)


def reload_class(class_obj):
    module_name = class_obj.__module__
    module = sys.modules[module_name]
    Log.debug("Reloading modules")
    for module_pycfile in get_modules(module):
        os.remove(os.path.join(os.path.dirname(module.__file__), module_pycfile))
        # pycfile = module.__file__
        pycfile = module_pycfile
        modulepath = pycfile.replace(".pyc", ".py")
        _module_name = pycfile.replace(".py*", "")
        print "importing " + os.path.join(os.path.dirname(module.__file__), modulepath)
        code = open(os.path.join(os.path.dirname(module.__file__), modulepath), 'rU').read()
        compile(code, _module_name, "exec")
        _module = sys.modules[_module_name]
        _module = reload(_module)

    return getattr(module, class_obj.__name__)


def register():
    topicManagers = []
    package = TelemetryLayer.topicmanagers
    for package in get_subpackages(TelemetryLayer.topicmanagers):
        path = os.path.join(os.path.dirname(TelemetryLayer.topicmanagers.__file__), package)
        if path not in sys.path:
            sys.path.append(path)
        module = None
        meta = {}
        Log.debug("Loading topic manager " + package)
        try:
            if sys.modules[package]:
                module = __import__(package)
                meta = module.classFactory()
                meta['class'] = reload_class(meta['class'])
        except AttributeError:
            pass
        except Exception as e:
            if "'" + package + "'" != str(e):
                Log.debug("Error loading topic manager " + str(e) + ' ' + package)
        finally:
            if module is None:
                module = __import__(package)
                meta = module.classFactory()

        meta['id'] = package
        topicManagers.append(meta)
    Log.debug("Done")
    return topicManagers

