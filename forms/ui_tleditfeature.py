# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'topicmanagers/ui_tleditfeature.ui'
#
# Created: Fri May  1 16:35:54 2015
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

class Ui_tlEditFeature(object):
    def setupUi(self, tlEditFeature):
        tlEditFeature.setObjectName(_fromUtf8("tlEditFeature"))
        tlEditFeature.resize(216, 190)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tlEditFeature.sizePolicy().hasHeightForWidth())
        tlEditFeature.setSizePolicy(sizePolicy)
        tlEditFeature.setMaximumSize(QtCore.QSize(500, 16777215))
        self.dockWidget = QtGui.QDockWidget(tlEditFeature)
        self.dockWidget.setEnabled(True)
        self.dockWidget.setGeometry(QtCore.QRect(0, 0, 481, 200))
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.payload = QtGui.QLabel(self.dockWidgetContents)
        self.payload.setGeometry(QtCore.QRect(80, 80, 101, 61))
        self.payload.setObjectName(_fromUtf8("payload"))
        self.dockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(tlEditFeature)
        QtCore.QMetaObject.connectSlotsByName(tlEditFeature)

    def retranslateUi(self, tlEditFeature):
        tlEditFeature.setWindowTitle(_translate("tlEditFeature", "Edit Feature", None))
        tlEditFeature.setToolTip(_translate("tlEditFeature", "<html><head/><body><p>Add Feature</p><p><br/></p></body></html>", None))
        tlEditFeature.setProperty("text", _translate("tlEditFeature", "Edit Feature", None))
        self.payload.setToolTip(_translate("tlEditFeature", "<html><head/><body><p>Hide from layer - payload values will only be visible via Features under the Broker (double click on a broker within the legend)</p></body></html>", None))
        self.payload.setText(_translate("tlEditFeature", "Payload", None))

