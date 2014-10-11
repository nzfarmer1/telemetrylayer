# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'topicmanagers/generic/ui_tlgenerictopicmanager.ui'
#
# Created: Sat Oct 11 20:27:24 2014
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

class Ui_tlGenericTopicManager(object):
    def setupUi(self, tlGenericTopicManager):
        tlGenericTopicManager.setObjectName(_fromUtf8("tlGenericTopicManager"))
        tlGenericTopicManager.resize(300, 348)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tlGenericTopicManager.sizePolicy().hasHeightForWidth())
        tlGenericTopicManager.setSizePolicy(sizePolicy)
        tlGenericTopicManager.setMaximumSize(QtCore.QSize(300, 16777215))
        self.Tabs = QtGui.QTabWidget(tlGenericTopicManager)
        self.Tabs.setGeometry(QtCore.QRect(0, 10, 301, 331))
        self.Tabs.setObjectName(_fromUtf8("Tabs"))
        self.tabTopics = QtGui.QWidget()
        self.tabTopics.setObjectName(_fromUtf8("tabTopics"))
        self.plainTextEdit = QtGui.QPlainTextEdit(self.tabTopics)
        self.plainTextEdit.setGeometry(QtCore.QRect(20, 30, 261, 191))
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.Tabs.addTab(self.tabTopics, _fromUtf8(""))

        self.retranslateUi(tlGenericTopicManager)
        self.Tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(tlGenericTopicManager)

    def retranslateUi(self, tlGenericTopicManager):
        tlGenericTopicManager.setWindowTitle(_translate("tlGenericTopicManager", "Edit Feature", None))
        tlGenericTopicManager.setToolTip(_translate("tlGenericTopicManager", "<html><head/><body><p>Add Feature</p><p><br/></p></body></html>", None))
        tlGenericTopicManager.setProperty("text", _translate("tlGenericTopicManager", "Edit Feature", None))
        self.plainTextEdit.setPlainText(_translate("tlGenericTopicManager", "This topic manager provides a list of MQTT $SYS topics and a set of default format functions for these.", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.tabTopics), _translate("tlGenericTopicManager", "Topics", None))

