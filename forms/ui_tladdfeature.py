# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/ui_tladdfeature.ui'
#
# Created: Tue Jun 16 22:13:35 2015
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

class Ui_tlAddFeature(object):
    def setupUi(self, tlAddFeature):
        tlAddFeature.setObjectName(_fromUtf8("tlAddFeature"))
        tlAddFeature.resize(300, 211)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tlAddFeature.sizePolicy().hasHeightForWidth())
        tlAddFeature.setSizePolicy(sizePolicy)
        tlAddFeature.setMaximumSize(QtCore.QSize(300, 16777215))
        self.setTopicLabel = QtGui.QLabel(tlAddFeature)
        self.setTopicLabel.setGeometry(QtCore.QRect(30, 40, 41, 16))
        self.setTopicLabel.setObjectName(_fromUtf8("setTopicLabel"))
        self.buttonAdd = QtGui.QPushButton(tlAddFeature)
        self.buttonAdd.setGeometry(QtCore.QRect(170, 140, 91, 32))
        self.buttonAdd.setObjectName(_fromUtf8("buttonAdd"))
        self.selectQoS = QtGui.QComboBox(tlAddFeature)
        self.selectQoS.setGeometry(QtCore.QRect(70, 96, 104, 26))
        self.selectQoS.setObjectName(_fromUtf8("selectQoS"))
        self.selectQoS.addItem(_fromUtf8(""))
        self.selectQoS.addItem(_fromUtf8(""))
        self.selectQoS.addItem(_fromUtf8(""))
        self.selectQoSLabel = QtGui.QLabel(tlAddFeature)
        self.selectQoSLabel.setGeometry(QtCore.QRect(30, 100, 51, 20))
        self.selectQoSLabel.setObjectName(_fromUtf8("selectQoSLabel"))
        self.chkBoxVisible = QtGui.QCheckBox(tlAddFeature)
        self.chkBoxVisible.setGeometry(QtCore.QRect(180, 100, 85, 18))
        self.chkBoxVisible.setChecked(True)
        self.chkBoxVisible.setObjectName(_fromUtf8("chkBoxVisible"))
        self.setTopic = QtGui.QLineEdit(tlAddFeature)
        self.setTopic.setGeometry(QtCore.QRect(70, 40, 181, 21))
        self.setTopic.setObjectName(_fromUtf8("setTopic"))
        self.setName = QtGui.QLineEdit(tlAddFeature)
        self.setName.setGeometry(QtCore.QRect(70, 70, 181, 21))
        self.setName.setObjectName(_fromUtf8("setName"))
        self.setNameLabel = QtGui.QLabel(tlAddFeature)
        self.setNameLabel.setGeometry(QtCore.QRect(30, 70, 41, 16))
        self.setNameLabel.setObjectName(_fromUtf8("setNameLabel"))
        self.buttonAddEdit = QtGui.QPushButton(tlAddFeature)
        self.buttonAddEdit.setGeometry(QtCore.QRect(60, 140, 111, 32))
        self.buttonAddEdit.setObjectName(_fromUtf8("buttonAddEdit"))

        self.retranslateUi(tlAddFeature)
        QtCore.QMetaObject.connectSlotsByName(tlAddFeature)

    def retranslateUi(self, tlAddFeature):
        tlAddFeature.setWindowTitle(_translate("tlAddFeature", "Add Feature", None))
        self.setTopicLabel.setToolTip(_translate("tlAddFeature", "<html><head/><body><p>Enter the MQTT Topic pattern - see http://mosquitto.org/man/mqtt-7.html</p></body></html>", None))
        self.setTopicLabel.setText(_translate("tlAddFeature", "Topic", None))
        self.buttonAdd.setText(_translate("tlAddFeature", "Add Topic", None))
        self.selectQoS.setToolTip(_translate("tlAddFeature", "<html><head/><body><p>Granted QoS (Not implemented by Mosquitto Library yet)</p></body></html>", None))
        self.selectQoS.setItemText(0, _translate("tlAddFeature", "QoS0", None))
        self.selectQoS.setItemText(1, _translate("tlAddFeature", "QoS1", None))
        self.selectQoS.setItemText(2, _translate("tlAddFeature", "QoS2", None))
        self.selectQoSLabel.setToolTip(_translate("tlAddFeature", "<html><head/><body><p>Devices require a custom name and must be assigned a type</p><p>The name will form the basis of the MQTT Topic that gets piublished.</p><p>For example Water Tank 1 will be converteed to the Topic name /digisense/water/tank/1</p></body></html>", None))
        self.selectQoSLabel.setText(_translate("tlAddFeature", "QoS", None))
        self.chkBoxVisible.setToolTip(_translate("tlAddFeature", "<html><head/><body><p>Display on layer, or access only via the Features list available Broker Settings or by double clicking on the Layer Group Name)</p></body></html>", None))
        self.chkBoxVisible.setText(_translate("tlAddFeature", "Visible", None))
        self.setTopic.setToolTip(_translate("tlAddFeature", "<html><head/><body><p>Enter the MQTT Topic pattern - see http://mosquitto.org/man/mqtt-7.html</p></body></html>", None))
        self.setName.setToolTip(_translate("tlAddFeature", "<html><head/><body><p>Enter the MQTT Topic pattern - see http://mosquitto.org/man/mqtt-7.html</p></body></html>", None))
        self.setNameLabel.setToolTip(_translate("tlAddFeature", "<html><head/><body><p>Enter the MQTT Topic pattern - see http://mosquitto.org/man/mqtt-7.html</p></body></html>", None))
        self.setNameLabel.setText(_translate("tlAddFeature", "Name", None))
        self.buttonAddEdit.setText(_translate("tlAddFeature", "Add and Edit", None))

