# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/ui_tlayerconfig.ui'
#
# Created: Fri Jun  5 15:20:04 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_tLayerConfig(object):
    def setupUi(self, tLayerConfig):
        tLayerConfig.setObjectName(_fromUtf8("tLayerConfig"))
        tLayerConfig.resize(253, 234)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tLayerConfig.sizePolicy().hasHeightForWidth())
        tLayerConfig.setSizePolicy(sizePolicy)
        tLayerConfig.setMaximumSize(QtCore.QSize(300, 16777215))
        tLayerConfig.setToolTip(_fromUtf8(""))
        self.selectBroker = QtGui.QComboBox(tLayerConfig)
        self.selectBroker.setGeometry(QtCore.QRect(47, 74, 151, 26))
        self.selectBroker.setObjectName(_fromUtf8("selectBroker"))
        self.selectBrokerLabel = QtGui.QLabel(tLayerConfig)
        self.selectBrokerLabel.setGeometry(QtCore.QRect(49, 62, 101, 16))
        self.selectBrokerLabel.setObjectName(_fromUtf8("selectBrokerLabel"))
        self.selectTopicManagerLabel = QtGui.QLabel(tLayerConfig)
        self.selectTopicManagerLabel.setGeometry(QtCore.QRect(49, 114, 151, 16))
        self.selectTopicManagerLabel.setObjectName(_fromUtf8("selectTopicManagerLabel"))
        self.selectTopicManager = QtGui.QComboBox(tLayerConfig)
        self.selectTopicManager.setGeometry(QtCore.QRect(47, 126, 151, 26))
        self.selectTopicManager.setObjectName(_fromUtf8("selectTopicManager"))
        self.title = QtGui.QLabel(tLayerConfig)
        self.title.setGeometry(QtCore.QRect(27, 24, 191, 16))
        self.title.setObjectName(_fromUtf8("title"))
        self.buttonCreate = QtGui.QPushButton(tLayerConfig)
        self.buttonCreate.setGeometry(QtCore.QRect(127, 184, 81, 32))
        self.buttonCreate.setObjectName(_fromUtf8("buttonCreate"))
        self.buttonCancel = QtGui.QPushButton(tLayerConfig)
        self.buttonCancel.setGeometry(QtCore.QRect(48, 184, 81, 32))
        self.buttonCancel.setObjectName(_fromUtf8("buttonCancel"))

        self.retranslateUi(tLayerConfig)
        QtCore.QMetaObject.connectSlotsByName(tLayerConfig)
        tLayerConfig.setTabOrder(self.selectBroker, self.selectTopicManager)
        tLayerConfig.setTabOrder(self.selectTopicManager, self.buttonCreate)
        tLayerConfig.setTabOrder(self.buttonCreate, self.buttonCancel)

    def retranslateUi(self, tLayerConfig):
        tLayerConfig.setWindowTitle(_translate("tLayerConfig", "Create Layer", None))
        self.selectBroker.setToolTip(_translate("tLayerConfig", "<html><head/><body><p>Select MQTT Broker from list (configure new if required)</p></body></html>", None))
        self.selectBrokerLabel.setToolTip(_translate("tLayerConfig", "<html><head/><body><p>Select broker from list</p></body></html>", None))
        self.selectBrokerLabel.setText(_translate("tLayerConfig", "Select Broker", None))
        self.selectTopicManagerLabel.setText(_translate("tLayerConfig", "Select Topic Manager", None))
        self.selectTopicManager.setToolTip(_translate("tLayerConfig", "Select the Topic Types able to be shown on this layer", None))
        self.title.setText(_translate("tLayerConfig", "Create new Telemetry Layer", None))
        self.buttonCreate.setText(_translate("tLayerConfig", "Create", None))
        self.buttonCancel.setText(_translate("tLayerConfig", "Cancel", None))

