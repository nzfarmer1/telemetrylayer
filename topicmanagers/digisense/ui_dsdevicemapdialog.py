# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'topicmanagers/digisense/ui_dsdevicemapdialog.ui'
#
# Created: Sat Oct 11 21:26:51 2014
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

class Ui_dsDeviceMapDialog(object):
    def setupUi(self, dsDeviceMapDialog):
        dsDeviceMapDialog.setObjectName(_fromUtf8("dsDeviceMapDialog"))
        dsDeviceMapDialog.resize(300, 366)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dsDeviceMapDialog.sizePolicy().hasHeightForWidth())
        dsDeviceMapDialog.setSizePolicy(sizePolicy)
        dsDeviceMapDialog.setMaximumSize(QtCore.QSize(300, 16777215))
        dsDeviceMapDialog.setProperty("currentTabName", _fromUtf8("Fubar"))
        self.deviceType = QtGui.QComboBox(dsDeviceMapDialog)
        self.deviceType.setGeometry(QtCore.QRect(30, 134, 241, 26))
        self.deviceType.setObjectName(_fromUtf8("deviceType"))
        self.deviceTypeLabel = QtGui.QLabel(dsDeviceMapDialog)
        self.deviceTypeLabel.setGeometry(QtCore.QRect(30, 120, 201, 20))
        self.deviceTypeLabel.setObjectName(_fromUtf8("deviceTypeLabel"))
        self.name = QtGui.QLineEdit(dsDeviceMapDialog)
        self.name.setGeometry(QtCore.QRect(70, 60, 201, 22))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name.sizePolicy().hasHeightForWidth())
        self.name.setSizePolicy(sizePolicy)
        self.name.setAcceptDrops(False)
        self.name.setObjectName(_fromUtf8("name"))
        self.nameLabel = QtGui.QLabel(dsDeviceMapDialog)
        self.nameLabel.setGeometry(QtCore.QRect(30, 64, 41, 16))
        self.nameLabel.setObjectName(_fromUtf8("nameLabel"))
        self.applyButton = QtGui.QPushButton(dsDeviceMapDialog)
        self.applyButton.setGeometry(QtCore.QRect(180, 310, 101, 32))
        self.applyButton.setObjectName(_fromUtf8("applyButton"))
        self.topic = QtGui.QLineEdit(dsDeviceMapDialog)
        self.topic.setGeometry(QtCore.QRect(70, 90, 201, 22))
        self.topic.setInputMethodHints(QtCore.Qt.ImhDialableCharactersOnly|QtCore.Qt.ImhEmailCharactersOnly|QtCore.Qt.ImhLowercaseOnly|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhUppercaseOnly|QtCore.Qt.ImhUrlCharactersOnly)
        self.topic.setObjectName(_fromUtf8("topic"))
        self.settingsLabel = QtGui.QLabel(dsDeviceMapDialog)
        self.settingsLabel.setGeometry(QtCore.QRect(30, 160, 51, 20))
        self.settingsLabel.setObjectName(_fromUtf8("settingsLabel"))
        self.deviceKeyLabel = QtGui.QLabel(dsDeviceMapDialog)
        self.deviceKeyLabel.setGeometry(QtCore.QRect(30, 14, 201, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.deviceKeyLabel.setFont(font)
        self.deviceKeyLabel.setTextFormat(QtCore.Qt.RichText)
        self.deviceKeyLabel.setObjectName(_fromUtf8("deviceKeyLabel"))
        self.topicLabel = QtGui.QLabel(dsDeviceMapDialog)
        self.topicLabel.setGeometry(QtCore.QRect(30, 92, 41, 20))
        self.topicLabel.setObjectName(_fromUtf8("topicLabel"))
        self.helpText = QtGui.QLabel(dsDeviceMapDialog)
        self.helpText.setGeometry(QtCore.QRect(30, 40, 211, 16))
        self.helpText.setTextFormat(QtCore.Qt.RichText)
        self.helpText.setObjectName(_fromUtf8("helpText"))
        self.parameterTable = QtGui.QTableWidget(dsDeviceMapDialog)
        self.parameterTable.setGeometry(QtCore.QRect(30, 180, 251, 121))
        self.parameterTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.parameterTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.parameterTable.setObjectName(_fromUtf8("parameterTable"))
        self.parameterTable.setColumnCount(0)
        self.parameterTable.setRowCount(0)
        self.parameterTable.horizontalHeader().setVisible(False)
        self.parameterTable.horizontalHeader().setHighlightSections(False)
        self.parameterTable.verticalHeader().setVisible(False)
        self.parameterTable.verticalHeader().setHighlightSections(False)
        self.deleteButton = QtGui.QPushButton(dsDeviceMapDialog)
        self.deleteButton.setGeometry(QtCore.QRect(49, 310, 121, 32))
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))

        self.retranslateUi(dsDeviceMapDialog)
        QtCore.QMetaObject.connectSlotsByName(dsDeviceMapDialog)

    def retranslateUi(self, dsDeviceMapDialog):
        dsDeviceMapDialog.setWindowTitle(_translate("dsDeviceMapDialog", "Device Mapping", None))
        self.deviceTypeLabel.setToolTip(_translate("dsDeviceMapDialog", "<html><head/><body><p>Set the device type from the list of available devices</p></body></html>", None))
        self.deviceTypeLabel.setText(_translate("dsDeviceMapDialog", "Device Type", None))
        self.name.setToolTip(_translate("dsDeviceMapDialog", "<html><head/><body><p>Provide a Name for this device - i.e. if it\'s a Tank level sensor in the top paddock, it could ne named Top Tank Level</p></body></html>", None))
        self.nameLabel.setToolTip(_translate("dsDeviceMapDialog", "<html><head/><body><p>Devices require a custom name and must be assigned a type</p><p>The name will form the basis of the MQTT Topic that gets piublished.</p><p>For example Water Tank 1 will be converteed to the Topic name /digisense/water/tank/1</p></body></html>", None))
        self.nameLabel.setText(_translate("dsDeviceMapDialog", "Name", None))
        self.applyButton.setText(_translate("dsDeviceMapDialog", "Apply", None))
        self.topic.setToolTip(_translate("dsDeviceMapDialog", "<html><head/><body><p>MQTT Topic name. This can be subscribed to and displayed in the Layer</p></body></html>", None))
        self.settingsLabel.setToolTip(_translate("dsDeviceMapDialog", "<html><head/><body><p>Configure the device settings</p></body></html>", None))
        self.settingsLabel.setText(_translate("dsDeviceMapDialog", "Settings", None))
        self.deviceKeyLabel.setToolTip(_translate("dsDeviceMapDialog", "<html><head/><body><p>Devices require a custom name and must be assigned a type</p><p><br/></p><p>The name will form the basis of the MQTT Topic that gets piublished.</p><p><br/></p><p>For example Water Tank 1 will be converteed to the Topic name /digisense/water/tank/1</p></body></html>", None))
        self.deviceKeyLabel.setText(_translate("dsDeviceMapDialog", "deviceKey", None))
        self.topicLabel.setToolTip(_translate("dsDeviceMapDialog", "<html><head/><body><p>MQTT Topic name. This can be subscribed to and displayed in the Layer</p></body></html>", None))
        self.topicLabel.setText(_translate("dsDeviceMapDialog", "Topic", None))
        self.helpText.setToolTip(_translate("dsDeviceMapDialog", "<html><head/><body><p>Devices require a custom name and must be assigned a type</p><p><br/></p><p>The name will form the basis of the MQTT Topic that gets piublished.</p><p><br/></p><p>For example Water Tank 1 will be converteed to the Topic name /digisense/water/tank/1</p></body></html>", None))
        self.helpText.setText(_translate("dsDeviceMapDialog", "Give this device a readable name", None))
        self.deleteButton.setText(_translate("dsDeviceMapDialog", "Delete Mapping", None))

