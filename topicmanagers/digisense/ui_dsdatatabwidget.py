# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'topicmanagers/digisense/ui_dsdatatabwidget.ui'
#
# Created: Thu Oct 23 19:38:40 2014
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
        self.Tabs.setGeometry(QtCore.QRect(10, 10, 351, 331))
        self.Tabs.setObjectName(_fromUtf8("Tabs"))
        self.dataTab = QtGui.QWidget()
        self.dataTab.setObjectName(_fromUtf8("dataTab"))
        self.tableWidget = QtGui.QTableWidget(self.dataTab)
        self.tableWidget.setGeometry(QtCore.QRect(15, 2, 201, 231))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.Tabs.addTab(self.dataTab, _fromUtf8(""))

        self.retranslateUi(Form)
        self.Tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.dataTab), _translate("Form", "Data", None))

