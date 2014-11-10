import sys, string, unittest, itertools
import xml.etree.ElementTree as ETree

# todo
# remove function
# add bool hasMap()

try:
 from TelemetryLayer.lib.tllogging import tlLogging as Log
except:
        import logging as Log



class dsDeviceType:
    """
    Class to represent the attributes of a physical device including:
    - Manufacturer
    - Model
    - I/O type
    - Device type i.e. temerature sensor/relay etc.
    - Lambda - conversion function
    """
    
    def __init__(self,device):
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
                return self.device.find('Params')

        except:
                return []

    def op(self):
        try:
                return self.device.find('Operation').text
        except:
                return None

    def _lambda(self,x):
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

    def find(self,tagName,default =""):
        try:
                result = self.device.find(tagName).text
        except:
                result = default

        return result

class dsDeviceTypes:

    def __init__(self,xml):
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
                    self.devices[_id] = dsDeviceType(device)

    def toString(self):
            return ETree.tostring(self.root)

    def values(self):
            return self.devices.values()


    def getDeviceTypeById(self,_id):
            if _id in self.devices:
                    return self.devices[_id]
            else:
                    return None

