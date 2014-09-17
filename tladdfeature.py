# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Add Feature Dialog
 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from ui_tladdfeature import Ui_tlAddFeature
from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from tlbrokers import tlBroker as Broker

# Add Help Button

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class tlAddFeature(QtGui.QDialog, Ui_tlAddFeature):
    
    def __init__(self,broker,topicType):
       super(tlAddFeature, self).__init__()
       self._broker = broker
       self._topicType = topicType
       
       self.setupUi()
       pass

    def setupUi(self):
       super(tlAddFeature,self).setupUi(self)
       topic = None
       self.selectTopic.addItem("Select a topic ...")
       for topic in self._broker.topics(self._topicType):
            self.selectTopic.addItem(topic['name'],topic)
       self.buttonAdd.clicked.connect(self._validateApply)
       self.buttonAdd.setEnabled(False)
       self.selectTopic.currentIndexChanged.connect(self._topicChanged)


    def getTopic(self):
        return self.selectTopic.itemData(self.selectTopic.currentIndex())


    def _topicChanged(self,idx):
        self.buttonAdd.setEnabled(idx >=0)

    def _validateApply(self):
        self.accept()

        


    
