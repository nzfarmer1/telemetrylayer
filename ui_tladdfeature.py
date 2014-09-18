# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_tladdfeature.ui'
#
# Created: Fri Sep 19 09:53:47 2014
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
        self.selectTopic = QtGui.QComboBox(tlAddFeature)
        self.selectTopic.setGeometry(QtCore.QRect(70, 60, 191, 26))
        self.selectTopic.setObjectName(_fromUtf8("selectTopic"))
        self.selectTopicLabel = QtGui.QLabel(tlAddFeature)
        self.selectTopicLabel.setGeometry(QtCore.QRect(30, 70, 41, 16))
        self.selectTopicLabel.setObjectName(_fromUtf8("selectTopicLabel"))
        self.buttonAdd = QtGui.QPushButton(tlAddFeature)
        self.buttonAdd.setGeometry(QtCore.QRect(170, 160, 101, 32))
        self.buttonAdd.setObjectName(_fromUtf8("buttonAdd"))

        self.retranslateUi(tlAddFeature)
        QtCore.QMetaObject.connectSlotsByName(tlAddFeature)

    def retranslateUi(self, tlAddFeature):
        tlAddFeature.setWindowTitle(_translate("tlAddFeature", "Add Feature", None))
        self.selectTopicLabel.setToolTip(_translate("tlAddFeature", "<html><head/><body><p>Devices require a custom name and must be assigned a type</p><p>The name will form the basis of the MQTT Topic that gets piublished.</p><p>For example Water Tank 1 will be converteed to the Topic name /digisense/water/tank/1</p></body></html>", None))
        self.selectTopicLabel.setText(_translate("tlAddFeature", "Topic", None))
        self.buttonAdd.setText(_translate("tlAddFeature", "Add Feature", None))

