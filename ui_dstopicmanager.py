# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dstopicmanager.ui'
#
# Created: Wed Oct  1 12:20:36 2014
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

class Ui_dsTopicManager(object):
    def setupUi(self, dsTopicManager):
        dsTopicManager.setObjectName(_fromUtf8("dsTopicManager"))
        dsTopicManager.resize(295, 380)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dsTopicManager.sizePolicy().hasHeightForWidth())
        dsTopicManager.setSizePolicy(sizePolicy)
        dsTopicManager.setMaximumSize(QtCore.QSize(295, 16777215))
        self.Tabs = QtGui.QTabWidget(dsTopicManager)
        self.Tabs.setGeometry(QtCore.QRect(0, 40, 295, 331))
        self.Tabs.setObjectName(_fromUtf8("Tabs"))
        self.tabDevices = QtGui.QWidget()
        self.tabDevices.setObjectName(_fromUtf8("tabDevices"))
        self.deviceTabs = QtGui.QTabWidget(self.tabDevices)
        self.deviceTabs.setGeometry(QtCore.QRect(5, 5, 281, 291))
        self.deviceTabs.setObjectName(_fromUtf8("deviceTabs"))
        self.tabPhysical = QtGui.QWidget()
        self.tabPhysical.setObjectName(_fromUtf8("tabPhysical"))
        self.tablePhysical = QtGui.QTableWidget(self.tabPhysical)
        self.tablePhysical.setGeometry(QtCore.QRect(5, 5, 265, 230))
        self.tablePhysical.setObjectName(_fromUtf8("tablePhysical"))
        self.tablePhysical.setColumnCount(0)
        self.tablePhysical.setRowCount(0)
        self.devicesRefresh = QtGui.QPushButton(self.tabPhysical)
        self.devicesRefresh.setGeometry(QtCore.QRect(165, 235, 110, 32))
        self.devicesRefresh.setObjectName(_fromUtf8("devicesRefresh"))
        self.deviceTabs.addTab(self.tabPhysical, _fromUtf8(""))
        self.tabLogical = QtGui.QWidget()
        self.tabLogical.setObjectName(_fromUtf8("tabLogical"))
        self.tableLogical = QtGui.QTableWidget(self.tabLogical)
        self.tableLogical.setGeometry(QtCore.QRect(5, 5, 265, 231))
        self.tableLogical.setObjectName(_fromUtf8("tableLogical"))
        self.tableLogical.setColumnCount(0)
        self.tableLogical.setRowCount(0)
        self.deviceTabs.addTab(self.tabLogical, _fromUtf8(""))
        self.tabDeviceTypes = QtGui.QWidget()
        self.tabDeviceTypes.setObjectName(_fromUtf8("tabDeviceTypes"))
        self.tableDeviceTypes = QtGui.QTableWidget(self.tabDeviceTypes)
        self.tableDeviceTypes.setGeometry(QtCore.QRect(5, 5, 265, 250))
        self.tableDeviceTypes.setObjectName(_fromUtf8("tableDeviceTypes"))
        self.tableDeviceTypes.setColumnCount(0)
        self.tableDeviceTypes.setRowCount(0)
        self.deviceTabs.addTab(self.tabDeviceTypes, _fromUtf8(""))
        self.Tabs.addTab(self.tabDevices, _fromUtf8(""))

        self.retranslateUi(dsTopicManager)
        self.Tabs.setCurrentIndex(0)
        self.deviceTabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(dsTopicManager)

    def retranslateUi(self, dsTopicManager):
        dsTopicManager.setWindowTitle(_translate("dsTopicManager", "Edit Feature", None))
        dsTopicManager.setToolTip(_translate("dsTopicManager", "<html><head/><body><p>Add Feature</p><p><br/></p></body></html>", None))
        dsTopicManager.setProperty("text", _translate("dsTopicManager", "Edit Feature", None))
        self.devicesRefresh.setText(_translate("dsTopicManager", "Refresh", None))
        self.deviceTabs.setTabText(self.deviceTabs.indexOf(self.tabPhysical), _translate("dsTopicManager", "Physical", None))
        self.deviceTabs.setTabText(self.deviceTabs.indexOf(self.tabLogical), _translate("dsTopicManager", "Logical", None))
        self.deviceTabs.setTabText(self.deviceTabs.indexOf(self.tabDeviceTypes), _translate("dsTopicManager", "Catalog", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.tabDevices), _translate("dsTopicManager", "Topics", None))

