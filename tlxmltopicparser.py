"""
/***************************************************************************
 tlXMLTopicParser
 
 Parse Topics from an XML definition
 ***************************************************************************/
"""

import sys, string, unittest, itertools
import xml.etree.ElementTree as ETree

from lib.tllogging import tlLogging as Log


class tlXMLTopicParser():

  def __init__(self,xml):

    self._topics = []
    self._root  = None
    self._xml = xml

    try:
      tree = ETree.parse(xml)
      self._root = tree.getroot()
      self._parse()
    except Exception as e:
      Log.debug("Unable to open/parse XML file: " + str(e))


  def _parse(self):
    for topic in self._root.iter('Topic'):
      self._topics.append({'topic': topic.get('value'), \
              'name':self._field(topic,'Name',True), \
              'desc':self._field(topic,'Description'), \
              'payload':self._field(topic,'Default'), \
              'units':self._field(topic,'Units'), \
              'type':self._field(topic,'Type',False,'$SYS'), \
              'qos':self._field(topic,'QoS',False,"1")})



  def _field(self,topic,field,required = False,default = ""):
    try:
      return topic.find(field).text
    except:
      if required:
        Log.critical("Error parsing " + self._xml + " No topic found")
      return default


  def getTopics(self):
    return self._topics
