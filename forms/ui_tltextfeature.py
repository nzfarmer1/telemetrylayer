# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/ui_tltextfeature.ui'
#
# Created: Mon Jun  8 15:55:46 2015
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

class Ui_tlTextFeature(object):
    def setupUi(self, tlTextFeature):
        tlTextFeature.setObjectName(_fromUtf8("tlTextFeature"))
        tlTextFeature.resize(315, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tlTextFeature.sizePolicy().hasHeightForWidth())
        tlTextFeature.setSizePolicy(sizePolicy)
        tlTextFeature.setMaximumSize(QtCore.QSize(360, 300))
        self.dockWidget = QtGui.QDockWidget(tlTextFeature)
        self.dockWidget.setEnabled(True)
        self.dockWidget.setGeometry(QtCore.QRect(0, 0, 360, 300))
        self.dockWidget.setMinimumSize(QtCore.QSize(360, 300))
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.payload = QtGui.QLabel(self.dockWidgetContents)
        self.payload.setGeometry(QtCore.QRect(20, 150, 331, 111))
        self.payload.setObjectName(_fromUtf8("payload"))
        self.symbol = QtGui.QLabel(self.dockWidgetContents)
        self.symbol.setGeometry(QtCore.QRect(20, 10, 128, 128))
        self.symbol.setMinimumSize(QtCore.QSize(128, 128))
        self.symbol.setMaximumSize(QtCore.QSize(128, 128))
        self.symbol.setText(_fromUtf8(""))
        self.symbol.setObjectName(_fromUtf8("symbol"))
        self.name = QtGui.QLabel(self.dockWidgetContents)
        self.name.setGeometry(QtCore.QRect(160, 50, 141, 51))
        self.name.setObjectName(_fromUtf8("name"))
        self.dockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(tlTextFeature)
        QtCore.QMetaObject.connectSlotsByName(tlTextFeature)

    def retranslateUi(self, tlTextFeature):
        tlTextFeature.setWindowTitle(_translate("tlTextFeature", "View Feature", None))
        tlTextFeature.setToolTip(_translate("tlTextFeature", "<html><head/><body><p>Add Feature</p><p><br/></p></body></html>", None))
        tlTextFeature.setProperty("text", _translate("tlTextFeature", "Edit Feature", None))
        self.payload.setToolTip(_translate("tlTextFeature", "Hide from layer - payload values will only be visible via Features under the Broker (double click on a broker within the legend)", None))
        self.payload.setText(_translate("tlTextFeature", "Payload", None))
        self.symbol.setToolTip(_translate("tlTextFeature", "<html><head/><body><p>Hide from layer - payload values will only be visible via Features under the Broker (double click on a broker within the legend)</p></body></html>", None))
        self.name.setToolTip(_translate("tlTextFeature", "Hide from layer - payload values will only be visible via Features under the Broker (double click on a broker within the legend)", None))
        self.name.setText(_translate("tlTextFeature", "Name", None))

