
"""
Dynamically load/reload topic manager packages
"""

import pkgutil
import os
import sys
import glob
from TelemetryLayer.lib.tllogging import tlLogging as Log
import TelemetryLayer.topicmanagers 

# Recipe from http://stackoverflow.com/users/66713/james-emerton

def get_subpackages(module):
    dir = os.path.dirname(module.__file__)
    def is_package(d):
        d = os.path.join(dir, d)
        return os.path.isdir(d) and glob.glob(os.path.join(d, '__init__.py*'))

    return filter(is_package, os.listdir(dir))

# Recipe adapted from http://stackoverflow.com/users/1736389/sam-p

def reload_class(class_obj):
    module_name = class_obj.__module__
    module = sys.modules[module_name]
    pycfile = module.__file__
    modulepath = pycfile.replace(".pyc", ".py")
    code=open(modulepath, 'rU').read()
    compile(code, module_name, "exec")
    module = reload(module)
    return getattr(module,class_obj.__name__)

def register():
        topicManagers = []
        package=TelemetryLayer.topicmanagers
        for package in get_subpackages(TelemetryLayer.topicmanagers):
            path = os.path.join(os.path.dirname(TelemetryLayer.topicmanagers.__file__),package)
            if path not in sys.path:
                sys.path.append(path)
            module = None
            meta ={}
            try:
                if sys.modules[package]:
                    module = __import__(package)
                    meta = module.classFactory()
                    meta['class'] =  reload_class(meta['class'])
            except Exception as e:
               Log.debug("Error loading topic manager " + str(e))
            finally:
                if module == None:
                    module = __import__(package)
                    meta = module.classFactory()

            meta['id'] = package
            topicManagers.append(meta)
        return topicManagers

