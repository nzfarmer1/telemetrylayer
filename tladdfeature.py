# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Add Feature Dialog
 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTimer, Qt
from PyQt4.QtGui import QRegExpValidator
from PyQt4.QtCore import QRegExp
from forms.ui_tladdfeature import Ui_tlAddFeature
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
    """
    Dialog to manage Add Features
    """

    def __init__(self, broker, topicManager):
        super(tlAddFeature, self).__init__()
        self._broker = broker
        self._topicManager = topicManager
        self._nameChanged = False

        self.setupUi()
        pass

    def setupUi(self):
        self.timer = QTimer()

        super(tlAddFeature, self).setupUi(self)

        self.setTopic.setValidator(QRegExpValidator(QRegExp("^[\$a-zA-Z0-9\-\_\/\-\#\+]+"), self))
        self.setTopic.textChanged.connect(self._topicChanged)
        self.setName.textEdited.connect(self._setNameChanged)

        self.buttonAdd.clicked.connect(self._validateApply)
        self.buttonAdd.setEnabled(False)
        
        
    def getVisible(self):
        if self.chkBoxVisible.checkState() == Qt.Checked:
            return 1
        return 0

    def getQoS(self):
        return int(self.selectQoS.currentIndex())

    def getTopic(self):
        if not len(self.setName.text()) > 0:
            self.setName.setText(self.setTopic.text())
        return {'topic':self.setTopic.text(),'name':self.setName.text()}
     
    def _setNameChanged(self,txt):
        self._nameChanged = len(txt) >0

    def _topicChanged(self, txt):
        self.buttonAdd.setEnabled(len(txt) >0)
        if len(txt) >0 and not self._nameChanged:
            self.setName.setText(txt.replace("/"," "))

    def _validateApply(self):
        self.accept()

        
    

    
