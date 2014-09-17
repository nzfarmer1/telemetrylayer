import sys, string, unittest, itertools
import xml.etree.ElementTree as ETree
import datetime
import json

try:
	if 'fsd.py' == sys.argv[0]:
		import logging as Log
	else:
		from tllogging import tlLogging as Log
except:
	from tllogging import tlLogging as Log


class dsDeviceMap:

	HIBYTE = 2
	LOBYTE = 3
	DTYPE  = 4
	DPIN  = 5

	@staticmethod	
	def createEmpty(deviceKey):
		data = {}
		data['deviceKey'] = deviceKey
		return dsDeviceMap(data)

	@staticmethod	
	def loads(deviceMap):
		try:
			return dsDeviceMap(json.loads(deviceMap))
		except ValueError:
			return None

	
	def __init__(self,data = {}):
		self.data = data
		if len(data) > 0:
			self.data = data
			self.parts = []
			if 'deviceKey' in self.data:
				self.parts = self.get('deviceKey').split("/")
	
	def getHiByte(self):
		if 'deviceKey' in self.data and len(self.parts)  > dsDeviceMap.DPIN:
			return self.parts[dsDeviceMap.HIBYTE]
		return None

	def getLoByte(self):
		if 'deviceKey' in self.data and len(self.parts)  > dsDeviceMap.DPIN:
			return self.parts[dsDeviceMap.LOBYTE]
		return None

	def getPin(self):
		if 'deviceKey' in self.data and len(self.parts)  > dsDeviceMap.DPIN:
			return self.parts[dsDeviceMap.DPIN]
		return None


	def getType(self):
		if 'deviceKey' in self.data and len(self.parts)  > dsDeviceMap.DPIN:
			dtype =  self.parts[dsDeviceMap.DTYPE]
		
			if dtype =='anou':
				return "ANALOG"
			
			if dtype =='anin':
				return "ANALOG"
	
			if dtype =='diin':
				return "DIGITAL"
	
			if dtype =='diou':
				return "DIGITAL"
		
		return 'UNKNOWN'

# Get direction
	def getIO(self):
		if 'deviceKey' in self.data and len(self.parts)  > dsDeviceMap.DPIN:
			dtype =  self.parts[dsDeviceMap.DTYPE]
		
		if dtype =='anou':
			return "OUT"
		
		if dtype =='anin':
			return "IN"

		if dtype =='diin':
			return "IN"

		if dtype =='diou':
			return "OUT"
		
		return 'UNKNOWN'

	def getUpdated(self):
		updated  =self.get('updated')
		if updated != None:
			return datetime.datetime.fromtimestamp(float(updated)).strftime('%H:%M:%S')
		return None
	
	def getStatus(self):
		return self.get('status')


	def setStatus(self,status):
		self.set('status',status)
	
	def getUnits(self):
		return self.get('units')


	def setUnits(self,units):
		self.set('units',units)


	def getName(self):
		return self.get('name')

	def getTopic(self):
		return self.get('topic')


	def getDeviceKey(self):
		return self.get('deviceKey')

# Return DeviceType (Catalog) Id
	def getDeviceTypeId(self):
		return self.get('deviceTypeId')

	def setDeviceTypeId(self,deviceTypeId):
		self.set('deviceTypeId',deviceTypeId)

	def unsetDeviceTypeId(self):
		self.unset('deviceTypeId')

	def isMapped(self):
		try:
			return  self.getDeviceTypeId() !=None and len(self.getName()) > 0 and len(self.getTopic()) > 0
		except:
			return False
			

	def getParams(self):
		return self.get('params',[])

	def getParam(self,name,default = None):
		params =  self.get('params')
		if params == None:
			return default
		try:
			return params[name]
		except:
			return default
	
	def getUpdated(self,raw = False):
		if raw:
			return self.get('updated')
		else:
			return datetime.datetime.fromtimestamp(int(self.get('updated'))).strftime('%Y-%m-%d %H:%M:%S')

	def get(self,attr,default = None):
		if attr in self.data:
			return self.data[attr]
		else:
			return default
	
	def set(self,attr,val = None):
		Log.debug("set " + attr + " " + str(val))
		self.data[attr] = val

	def unset(self,attr):
		try:
			del self.data[attr]
		except:
			pass		
		
	def dumps(self):
		return json.dumps(self.data)
		



class dsDeviceMaps:
	
	@staticmethod
	def encode(maps):
		return json.dumps(maps)

	@staticmethod
	def decode(maps):
#		Log.debug(json.loads(str(maps)))
		try:
			return json.loads(str(maps))
		except ValueError:
			return None

	@staticmethod
	def loads(maps):
#		Log.debug(json.loads(str(maps)))
		return dsDeviceMaps(json.loads(str(maps)))
	
	def __init__(self,devicemaps = []):
		self.devicemaps = devicemaps
		self.data = []
		for devicemap in devicemaps:
			#Log.debug(dsDeviceMap(devicemap))
			self.data.append(dsDeviceMap(devicemap)) 
	
	def dumps(self):
		return json.dumps(self.data)
		
	def getDeviceMaps(self):
		return self.data
	
	def list(self):
		return list(self.devicemaps)
		
	def items(self):
		return self.data
	
