import sys, string, unittest, itertools
import xml.etree.ElementTree as ETree

# todo
# remove function
# add bool hasMap()

try:
    from TelemetryLayer.lib.tllogging import tlLogging as Log
except:
    import logging as Log

"""
Devices are definitions of an agSense device
Can be used for relays or RETs or RTDs (sensors)

Can have 0 or more parameters able to be set via PyQt widgets

"""

class agParam:
    """
    Instance of a parameter to create a PyQt widget.
    Includes, name, value, min, max, widget etc.
    """
    
    def __init__(self,param):
        self.param = param

    def name(self):
        return self._attr("name")

    def widget(self):
        return self._attr("widget")

    def title(self):
        return self._attr("title")

    def desc(self):
        return self._attr("description")

    def _attr(self,key):
        try:
            return self.param.get(key)
        except:
            return None # raise exception

    def value(self):
        if self._find('Value') is None:
            return self._find('Default')
        return self._find('Value')

    def default(self):
        return self._find('Default')

    def units(self):
        return self._find('Units')

    def interval(self):
        return self._find('Interval')

    def min(self):
        return self._find('Min')

    def max(self):
        return self._find('Max')

    def type(self):
        return self._find('Type')

    def _find(self,key):
        try:
            return self.param.find(key).text
        except:
            return None
        
    def dump(self):
        _param = {'name': self.name(), 'type': self.type(),'widget':self.widget(),'title':self.title(),'desc':self.desc()}
        for p in self.param:
            _param[p.tag.lower()] = p.text
        return _param
        

class agParams:
    """
    Container for agParam(s)
    """
    def __init__(self, params):
        self.params = {}
        for param in params.getiterator():
            _p = agParam(param)
            try:
                if not _p.name():
                    continue
                self.params[_p.name()]  = _p
            except:
                # I know ...
                pass
        
    def __iter__(self):
        return self.params.itervalues();

    def dump(self):
        params = []
        for param in self:
            params.append(param.dump())
        return params
        pass

class agDevice:
    """
    Class to represent the attributes of a physical device including:
    - Manufacturer
    - Model
    - I/O type
    - Device type i.e. temerature sensor/relay etc.
    - Lambda - conversion function
    """

    def __init__(self, device):
        self.device = device

    def id(self):
        try:
            return self.device.get('id')
        except:
            return 'Unknown ID'

    def manufacturer(self):
        try:
            return self.device.find('Manufacturer').text
        except:
            return None

    def name(self):
        try:
            return self.device.find('Name').text
        except:
            return None

    def model(self):
        try:
            return self.device.find('Model').text
        except:
            return None

    def units(self):
        try:
            return self.device.find('Units').text
        except:
            return None

    def type(self):
        try:
            return self.device.get('type')
        except:
            return None

    def params(self):
        try:
            return agParams(self.device.find('Params'))
        except Exception as e:
            return []

    def op(self):
        try:
            return self.device.find('Operation').text
        except:
            return None

    def topic(self):
        try:
            return self.device.find('Topic').text
        except:
            return None

    def _lambda(self, x):
        try:
            l = self.device.find('Lambda').text
            # perform regex for paramaters!!!
            f = eval("lambda " + l)
            if 'function' in str(type(f)):
                return f(x)
            else:
                return x
        except TypeError as e:
            Log.debug('Type Error ' + str(e))
            return x
        except Exception as e:
            Log.debug(e)
            return x

    def find(self, tagName, default=""):
        try:
            result = self.device.find(tagName).text
        except:
            result = default
        return result


class agDeviceList:
    """
    Container - List of agDevices
    
    
    """
    def __init__(self, xml):
        self.devices = {}

        if xml[0] == '<':
            Log.debug('Parsing XML from string')
            self.root = ETree.fromstring(xml)
        else:
            try:
                tree = ETree.parse(xml)
                self.root = tree.getroot()
            except Exception as e:
                Log.debug("Unable to open/parse XML file: " + str(e))

        for device in self.root.iter('Device'):
            _id = device.get('id')
            self.devices[_id] = agDevice(device)

    def toString(self):
        return ETree.tostring(self.root)

    def values(self):
        return self.devices.values()

    def getDeviceById(self, _id):
        if _id in self.devices:
            return self.devices[_id]
        else:
            return None

    def keys(self):
        return self.devices.iter()
        
    def items(self):
        return self.devices.values()
    
    def __iter__(self):
        return self.devices.itervalues()
    
    def __len__(self):
        return len(self.devices)
            

if __name__ == '__main__':
    print "Testing " + sys.argv[0] + " with " +  sys.argv[1]
    xml = open(sys.argv[1]).read()
    agl  = agDeviceList(sys.argv[1])
#    print agl.values()

    for d in agl:
        print d.op()
        
        for p in d.params():
            print p.name()
            print p.value()
        print "\n";
        print d.params().dump()