# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'topicmanagers/digisense/ui_dsdatatabwidget.ui'
#
# Created: Tue Oct 28 15:44:33 2014
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(464, 351)
        self.Tabs = QtGui.QTabWidget(Form)
        self.Tabs.setGeometry(QtCore.QRect(10, 10, 441, 331))
        self.Tabs.setObjectName(_fromUtf8("Tabs"))
        self.dataTab = QtGui.QWidget()
        self.dataTab.setObjectName(_fromUtf8("dataTab"))
        self.tableWidget = QtGui.QTableWidget(self.dataTab)
        self.tableWidget.setGeometry(QtCore.QRect(15, 2, 251, 231))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.comboInterval = QtGui.QComboBox(self.dataTab)
        self.comboInterval.setGeometry(QtCore.QRect(280, 20, 111, 26))
        self.comboInterval.setObjectName(_fromUtf8("comboInterval"))
        self.comboInterval.addItem(_fromUtf8(""))
        self.comboInterval.addItem(_fromUtf8(""))
        self.comboInterval.addItem(_fromUtf8(""))
        self.comboInterval.addItem(_fromUtf8(""))
        self.comboInterval.addItem(_fromUtf8(""))
        self.comboInterval.addItem(_fromUtf8(""))
        self.comboInterval.addItem(_fromUtf8(""))
        self.comboInterval.addItem(_fromUtf8(""))
        self.comboDuration = QtGui.QComboBox(self.dataTab)
        self.comboDuration.setGeometry(QtCore.QRect(280, 80, 111, 26))
        self.comboDuration.setObjectName(_fromUtf8("comboDuration"))
        self.btnRefresh = QtGui.QPushButton(self.dataTab)
        self.btnRefresh.setGeometry(QtCore.QRect(280, 140, 114, 32))
        self.btnRefresh.setObjectName(_fromUtf8("btnRefresh"))
        self.labelInterval = QtGui.QLabel(self.dataTab)
        self.labelInterval.setGeometry(QtCore.QRect(280, 0, 62, 16))
        self.labelInterval.setObjectName(_fromUtf8("labelInterval"))
        self.labelDuration = QtGui.QLabel(self.dataTab)
        self.labelDuration.setGeometry(QtCore.QRect(280, 60, 62, 16))
        self.labelDuration.setObjectName(_fromUtf8("labelDuration"))
        self.btnExport = QtGui.QPushButton(self.dataTab)
        self.btnExport.setGeometry(QtCore.QRect(280, 190, 114, 32))
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.Tabs.addTab(self.dataTab, _fromUtf8(""))

        self.retranslateUi(Form)
        self.Tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.comboInterval.setToolTip(_translate("Form", "<html><head/><body><p>Set the interval between each update (or tick for every update)</p></body></html>", None))
        self.comboInterval.setItemText(0, _translate("Form", "Tick", None))
        self.comboInterval.setItemText(1, _translate("Form", "1 Minute", None))
        self.comboInterval.setItemText(2, _translate("Form", "5 Minute", None))
        self.comboInterval.setItemText(3, _translate("Form", "15 Minute", None))
        self.comboInterval.setItemText(4, _translate("Form", "30 Minute", None))
        self.comboInterval.setItemText(5, _translate("Form", "1 Hour", None))
        self.comboInterval.setItemText(6, _translate("Form", "4 Hour", None))
        self.comboInterval.setItemText(7, _translate("Form", "Daily", None))
        self.comboDuration.setToolTip(_translate("Form", "<html><head/><body><p>Time since first record</p></body></html>", None))
        self.btnRefresh.setToolTip(_translate("Form", "<html><head/><body><p>Refresh</p></body></html>", None))
        self.btnRefresh.setText(_translate("Form", "Refresh", None))
        self.labelInterval.setToolTip(_translate("Form", "<html><head/><body><p>Set the interval between each update (or tick for every update)</p></body></html>", None))
        self.labelInterval.setText(_translate("Form", "Interval", None))
        self.labelDuration.setToolTip(_translate("Form", "<html><head/><body><p>Time since first record</p></body></html>", None))
        self.labelDuration.setText(_translate("Form", "Duration", None))
        self.btnExport.setToolTip(_translate("Form", "<html><head/><body><p>Export data (.csv)</p></body></html>", None))
        self.btnExport.setText(_translate("Form", "Export", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.dataTab), _translate("Form", "Data", None))

