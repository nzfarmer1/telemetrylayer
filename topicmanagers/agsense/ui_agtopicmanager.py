# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'topicmanagers/agsense/ui_agtopicmanager.ui'
#
# Created: Tue Mar 24 14:11:04 2015
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

class Ui_agTopicManager(object):
    def setupUi(self, agTopicManager):
        agTopicManager.setObjectName(_fromUtf8("agTopicManager"))
        agTopicManager.resize(295, 391)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(agTopicManager.sizePolicy().hasHeightForWidth())
        agTopicManager.setSizePolicy(sizePolicy)
        agTopicManager.setMaximumSize(QtCore.QSize(295, 16777215))
        self.Tabs = QtGui.QTabWidget(agTopicManager)
        self.Tabs.setGeometry(QtCore.QRect(0, 40, 295, 331))
        self.Tabs.setObjectName(_fromUtf8("Tabs"))
        self.tabDevices = QtGui.QWidget()
        self.tabDevices.setObjectName(_fromUtf8("tabDevices"))
        self.devicesRefresh = QtGui.QPushButton(self.tabDevices)
        self.devicesRefresh.setGeometry(QtCore.QRect(170, 260, 110, 32))
        self.devicesRefresh.setObjectName(_fromUtf8("devicesRefresh"))
        self.tableDevices = QtGui.QTableWidget(self.tabDevices)
        self.tableDevices.setGeometry(QtCore.QRect(10, 20, 265, 230))
        self.tableDevices.setObjectName(_fromUtf8("tableDevices"))
        self.tableDevices.setColumnCount(0)
        self.tableDevices.setRowCount(0)
        self.Tabs.addTab(self.tabDevices, _fromUtf8(""))

        self.retranslateUi(agTopicManager)
        self.Tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(agTopicManager)

    def retranslateUi(self, agTopicManager):
        agTopicManager.setWindowTitle(_translate("agTopicManager", "Edit Feature", None))
        agTopicManager.setToolTip(_translate("agTopicManager", "<html><head/><body><p>Add Feature</p><p><br/></p></body></html>", None))
        agTopicManager.setProperty("text", _translate("agTopicManager", "Edit Feature", None))
        self.devicesRefresh.setText(_translate("agTopicManager", "Refresh", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.tabDevices), _translate("agTopicManager", "Topics", None))

