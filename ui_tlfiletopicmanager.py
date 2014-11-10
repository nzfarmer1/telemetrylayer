# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_tlfiletopicmanager.ui'
#
# Created: Wed Sep 10 08:16:19 2014
# by: PyQt4 UI code generator 4.10.4
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


class Ui_tlFileTopicManager(object):
    def setupUi(self, tlFileTopicManager):
        tlFileTopicManager.setObjectName(_fromUtf8("tlFileTopicManager"))
        tlFileTopicManager.resize(300, 348)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tlFileTopicManager.sizePolicy().hasHeightForWidth())
        tlFileTopicManager.setSizePolicy(sizePolicy)
        tlFileTopicManager.setMaximumSize(QtCore.QSize(300, 16777215))
        self.Tabs = QtGui.QTabWidget(tlFileTopicManager)
        self.Tabs.setGeometry(QtCore.QRect(0, 10, 301, 331))
        self.Tabs.setObjectName(_fromUtf8("Tabs"))
        self.tabTopics = QtGui.QWidget()
        self.tabTopics.setObjectName(_fromUtf8("tabTopics"))
        self.listTopicsTable = QtGui.QTableWidget(self.tabTopics)
        self.listTopicsTable.setGeometry(QtCore.QRect(15, 20, 261, 241))
        self.listTopicsTable.setObjectName(_fromUtf8("listTopicsTable"))
        self.listTopicsTable.setColumnCount(0)
        self.listTopicsTable.setRowCount(0)
        self.selectFileButton = QtGui.QPushButton(self.tabTopics)
        self.selectFileButton.setGeometry(QtCore.QRect(170, 270, 110, 32))
        self.selectFileButton.setObjectName(_fromUtf8("selectFileButton"))
        self.reloadFileButton = QtGui.QPushButton(self.tabTopics)
        self.reloadFileButton.setGeometry(QtCore.QRect(70, 270, 91, 32))
        self.reloadFileButton.setObjectName(_fromUtf8("reloadFileButton"))
        self.fileNameLabel = QtGui.QLabel(self.tabTopics)
        self.fileNameLabel.setGeometry(QtCore.QRect(20, 0, 271, 16))
        self.fileNameLabel.setObjectName(_fromUtf8("fileNameLabel"))
        self.Tabs.addTab(self.tabTopics, _fromUtf8(""))

        self.retranslateUi(tlFileTopicManager)
        self.Tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(tlFileTopicManager)

    def retranslateUi(self, tlFileTopicManager):
        tlFileTopicManager.setWindowTitle(_translate("tlFileTopicManager", "Edit Feature", None))
        tlFileTopicManager.setToolTip(
            _translate("tlFileTopicManager", "<html><head/><body><p>Add Feature</p><p><br/></p></body></html>", None))
        tlFileTopicManager.setProperty("text", _translate("tlFileTopicManager", "Edit Feature", None))
        self.selectFileButton.setText(_translate("tlFileTopicManager", "Select File", None))
        self.reloadFileButton.setText(_translate("tlFileTopicManager", "Reload", None))
        self.fileNameLabel.setText(_translate("tlFileTopicManager", "No file selected", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.tabTopics), _translate("tlFileTopicManager", "Topics", None))

