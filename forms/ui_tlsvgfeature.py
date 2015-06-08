# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/ui_tlsvgfeature.ui'
#
# Created: Mon Jun  8 12:12:53 2015
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

class Ui_tlSVGFeature(object):
    def setupUi(self, tlSVGFeature):
        tlSVGFeature.setObjectName(_fromUtf8("tlSVGFeature"))
        tlSVGFeature.resize(360, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tlSVGFeature.sizePolicy().hasHeightForWidth())
        tlSVGFeature.setSizePolicy(sizePolicy)
        tlSVGFeature.setMaximumSize(QtCore.QSize(360, 300))
        self.dockWidget = QtGui.QDockWidget(tlSVGFeature)
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
        self.dockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(tlSVGFeature)
        QtCore.QMetaObject.connectSlotsByName(tlSVGFeature)

    def retranslateUi(self, tlSVGFeature):
        tlSVGFeature.setWindowTitle(_translate("tlSVGFeature", "View Feature", None))
        tlSVGFeature.setToolTip(_translate("tlSVGFeature", "<html><head/><body><p>Add Feature</p><p><br/></p></body></html>", None))
        tlSVGFeature.setProperty("text", _translate("tlSVGFeature", "Edit Feature", None))
        self.payload.setToolTip(_translate("tlSVGFeature", "Hide from layer - payload values will only be visible via Features under the Broker (double click on a broker within the legend)", None))
        self.payload.setText(_translate("tlSVGFeature", "Payload", None))
        self.symbol.setToolTip(_translate("tlSVGFeature", "<html><head/><body><p>Hide from layer - payload values will only be visible via Features under the Broker (double click on a broker within the legend)</p></body></html>", None))

