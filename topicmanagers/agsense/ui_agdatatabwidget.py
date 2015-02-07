# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'topicmanagers/agsense/ui_agdatatabwidget.ui'
#
# Created: Tue Feb  3 14:40:13 2015
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
        self.Tabs.setGeometry(QtCore.QRect(10, 10, 441, 291))
        self.Tabs.setObjectName(_fromUtf8("Tabs"))
        self.dataTab = QtGui.QWidget()
        self.dataTab.setObjectName(_fromUtf8("dataTab"))
        self.tableWidget = QtGui.QTableWidget(self.dataTab)
        self.tableWidget.setGeometry(QtCore.QRect(15, 2, 251, 231))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.selectInterval = QtGui.QComboBox(self.dataTab)
        self.selectInterval.setGeometry(QtCore.QRect(280, 20, 111, 26))
        self.selectInterval.setObjectName(_fromUtf8("selectInterval"))
        self.selectDuration = QtGui.QComboBox(self.dataTab)
        self.selectDuration.setGeometry(QtCore.QRect(280, 80, 111, 26))
        self.selectDuration.setObjectName(_fromUtf8("selectDuration"))
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
        self.chartTab = QtGui.QWidget()
        self.chartTab.setObjectName(_fromUtf8("chartTab"))
        self.selectDurationc = QtGui.QComboBox(self.chartTab)
        self.selectDurationc.setGeometry(QtCore.QRect(130, 200, 111, 26))
        self.selectDurationc.setObjectName(_fromUtf8("selectDurationc"))
        self.selectIntervalc = QtGui.QComboBox(self.chartTab)
        self.selectIntervalc.setGeometry(QtCore.QRect(10, 200, 111, 26))
        self.selectIntervalc.setObjectName(_fromUtf8("selectIntervalc"))
        self.btnRefreshc = QtGui.QPushButton(self.chartTab)
        self.btnRefreshc.setGeometry(QtCore.QRect(280, 200, 114, 32))
        self.btnRefreshc.setObjectName(_fromUtf8("btnRefreshc"))
        self.graphicsView = QtGui.QGraphicsView(self.chartTab)
        self.graphicsView.setGeometry(QtCore.QRect(6, 0, 391, 200))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.Tabs.addTab(self.chartTab, _fromUtf8(""))
        self.configTab = QtGui.QWidget()
        self.configTab.setObjectName(_fromUtf8("configTab"))
        self.tblParams = QtGui.QTableWidget(self.configTab)
        self.tblParams.setGeometry(QtCore.QRect(50, 20, 256, 161))
        self.tblParams.setObjectName(_fromUtf8("tblParams"))
        self.tblParams.setColumnCount(0)
        self.tblParams.setRowCount(0)
        self.btnApply = QtGui.QPushButton(self.configTab)
        self.btnApply.setGeometry(QtCore.QRect(200, 190, 114, 32))
        self.btnApply.setObjectName(_fromUtf8("btnApply"))
        self.label = QtGui.QLabel(self.configTab)
        self.label.setGeometry(QtCore.QRect(50, 0, 261, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.btnReload = QtGui.QPushButton(self.configTab)
        self.btnReload.setGeometry(QtCore.QRect(80, 190, 114, 32))
        self.btnReload.setObjectName(_fromUtf8("btnReload"))
        self.Tabs.addTab(self.configTab, _fromUtf8(""))

        self.retranslateUi(Form)
        self.Tabs.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.Tabs.setAccessibleName(_translate("Form", "Chart", None))
        self.selectInterval.setToolTip(_translate("Form", "<html><head/><body><p>Set the interval between each update (or tick for every update)</p></body></html>", None))
        self.selectDuration.setToolTip(_translate("Form", "<html><head/><body><p>Time since first record</p></body></html>", None))
        self.btnRefresh.setToolTip(_translate("Form", "<html><head/><body><p>Refresh</p></body></html>", None))
        self.btnRefresh.setText(_translate("Form", "Refresh", None))
        self.labelInterval.setToolTip(_translate("Form", "<html><head/><body><p>Set the interval between each update (or tick for every update)</p></body></html>", None))
        self.labelInterval.setText(_translate("Form", "Interval", None))
        self.labelDuration.setToolTip(_translate("Form", "<html><head/><body><p>Time since first record</p></body></html>", None))
        self.labelDuration.setText(_translate("Form", "Duration", None))
        self.btnExport.setToolTip(_translate("Form", "<html><head/><body><p>Export data (.csv)</p></body></html>", None))
        self.btnExport.setText(_translate("Form", "Export", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.dataTab), _translate("Form", "Data", None))
        self.selectDurationc.setToolTip(_translate("Form", "<html><head/><body><p>Time since first record</p></body></html>", None))
        self.selectIntervalc.setToolTip(_translate("Form", "<html><head/><body><p>Set the interval between each update (or tick for every update)</p></body></html>", None))
        self.btnRefreshc.setToolTip(_translate("Form", "<html><head/><body><p>Refresh</p></body></html>", None))
        self.btnRefreshc.setText(_translate("Form", "Draw", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.chartTab), _translate("Form", "Chart", None))
        self.btnApply.setToolTip(_translate("Form", "<html><head/><body><p>Apply settings for device.</p></body></html>", None))
        self.btnApply.setText(_translate("Form", "Apply", None))
        self.label.setText(_translate("Form", "Update server based configuration", None))
        self.btnReload.setToolTip(_translate("Form", "<html><head/><body><p>Refresh local copies of all devices for this AgSense broker.</p></body></html>", None))
        self.btnReload.setText(_translate("Form", "Reload", None))
        self.Tabs.setTabText(self.Tabs.indexOf(self.configTab), _translate("Form", "Configure", None))

