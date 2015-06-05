# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tLayerConfig

 New Layer Dialog

 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from forms.ui_tlayerconfig import Ui_tLayerConfig
from tlbrokers import tlBrokers as Brokers
from lib.tlsettings import tlSettings as Settings
from lib.tllogging import tlLogging as Log
from tltopicmanagerfactory import tlTopicManagerFactory as tmFactory

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


class tLayerConfig(QtGui.QDialog, Ui_tLayerConfig):
    """
    Dialog to support creation of a new Telemetry Layer
    """

    def __init__(self, creator):
        super(tLayerConfig, self).__init__()

        self._creator = creator
        self._brokers = Brokers.instance().list()
        self._brokers = Brokers.instance().list()
        self._invalidTypes = []
        self.setupUi()
        self.selectBroker.currentIndexChanged.connect(self._brokerChanged)
#        self.selectTopicManager.currentIndexChanged.connect(self._topicManagerChanged)


    def setupUi(self):
        super(tLayerConfig, self).setupUi(self)

        self.selectBroker.addItem("Select Broker ...", None)
        for broker in self._brokers: # Note: If NOT already Layer in Layers!
            self.selectBroker.addItem(broker.name(), broker)
        self._brokerChanged(0)
        self.buttonCreate.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)
        self.buttonCreate.setEnabled(False)

        for tm in tmFactory.getTopicManagers():
            self.selectTopicManager.addItem(tm.name(),tm)
 
        return

    def _brokerChanged(self, idx):
 
        broker = self.selectBroker.itemData(idx)

        self.buttonCreate.setEnabled(idx > 0)
        self.selectTopicManager.setEnabled(idx > 0)


    def getBroker(self):
        return self.selectBroker.itemData(self.selectBroker.currentIndex())

    def getTopicManager(self):
        return self.selectTopicManager.itemData(self.selectTopicManager.currentIndex())


    def accept(self):
        super(tLayerConfig, self).accept()
        

    
