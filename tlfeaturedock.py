# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlBrokerConfig
 
 Configure individual Brokers
 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui, QtSvg
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSvg import *
from qgis.core import *
import webbrowser,pickle,json

from lib.tlsettings import tlSettings as Settings
from lib.tlsettings import tlConstants as Constants
from lib.tllogging import tlLogging as Log
from forms.ui_tltextfeature import Ui_tlTextFeature
from forms.ui_tlsvgfeature import Ui_tlSVGFeature

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

_symbols = {}  # store symbols


def ActiveLayerSymbolPixmap(layer,feat):
    """
     Return active layer symbol for feature as a pixmap
     use cache
    """

    r       = layer.rendererV2()
    items   = r.legendSymbologyItems(QSize(32,32))
    pos     = map(lambda(rule):
                rule.isFilterOK(feat), r.rootRule().children()).index(True,0)

    (state,pixmap) = items[pos]

    if not _symbols.has_key(state):
        symbol  = r.rootRule().children()[pos].symbol().clone()
        symbol.setSize(50)
        symbol.symbolLayer(0).setVerticalAnchorPoint(QgsMarkerSymbolLayerV2.VCenter)
        symbol.symbolLayer(0).setHorizontalAnchorPoint(QgsMarkerSymbolLayerV2.HCenter)
        image = symbol.bigSymbolPreviewImage()
        _symbols[state] = QPixmap.fromImage(image)

    return _symbols[state]


class tlFeatureDock(QDialog):
    """
    Dialog to manage a feature within a dock
    """

    def __init__(self, iface, tlayer, feature,show = True):
        self._iface =iface
        self._feature = feature
        self._tlayer = tlayer
        self._layer =tlayer.layer()
        self._key = 'featureDock-' + str(self._layer.id()) + '-' + str(feature.id())
        super(tlFeatureDock,self).__init__()
        
        self.setupUi(self)

        self.dockWidget.setWindowTitle(feature['name'])
        self.dockWidget.setAllowedAreas(Qt.AllDockWidgetAreas)
        self._iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
        self.dockWidget.hide()
        self.dockWidget.setFloating(True)
        self.dockWidget.resize(300,300)
        self.dockWidget.move(300,300)
        self.dockWidget.setObjectName(str(self))
        self._palyr = QgsPalLayerSettings()
        self._palyr.readFromLayer(tlayer.layer())
        self._tlayer.featureUpdated.connect(self._featureUpdated)
        self.dockWidget.visibilityChanged.connect(self._visibilityChanged)
        self.dockWidget.dockLocationChanged.connect(self._dockLocationChanged)
       
        self.dockWidget.resizeEvent = self._dockLocationChanged
        
        if show:
            self.featureUpdated(self._tlayer,feature)
            self.dockWidget.show()
        #self.payload.setAutoFillBackground(True)
    
    
    def _featureUpdated(self,tlayer,feat):
        if not self.isVisible():
            return
        self.saveGeometry()
        if feat.id() != self._feature.id():
            return
        
        self.featureUpdated(tlayer,feat)

    def featureUpdated(self,tlayer,feat):
        pass
    
    
    def saveGeometry(self):
            geometry = self.dockWidget.saveGeometry()
            if self._geometry != geometry:
                self._geometry = geometry
                Settings.setp(self._key,pickle.dumps(geometry))
                QgsProject.instance().setDirty(True)
                Log.debug("dirty")
    
    def restoreGeometry(self):
            self._geometry = pickle.loads(Settings.getp(self._key,pickle.dumps(None)))
            if self._geometry is None:
                return
            self.dockWidget.restoreGeometry(self._geometry)

    def featureId(self):
        return self._feature.id()
    
    def layerId(self):
        return self._layer.id()
    
    def show(self):
        self.dockWidget.show()

    def close(self):
        self.dockWidget.close()

    def isVisible(self):
        return self.dockWidget.isVisible()

    def _dockLocationChanged(self,area = None):
        self.saveGeometry()

    def _visibilityChanged(self,visible):
        visible = visible | self.isVisible()
#        Log.debug("Visibility changed " + str(self.isVisible()))
#        Log.debug("Focus" + str(self.dockWidget.hasFocus()))
#        Log.debug(self.frameSize())
#        Log.debug(self.dockWidget.frameSize())
        if not visible:
            self.saveGeometry()
        else:
            self.restoreGeometry()
        pass
    

class tlFormFeatureDock(tlFeatureDock):

    def __init__(self, iface, tlayer, feature,show = False):
        super(tlFormFeatureDock,self).__init__(iface,tlayer,feature,show)

    def setupUi(self, tlFormFeature):
        tlFormFeature.setObjectName(_fromUtf8("tlFormFeature"))
        tlFormFeature.resize(300, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tlFormFeature.sizePolicy().hasHeightForWidth())
        tlFormFeature.setSizePolicy(sizePolicy)
        tlFormFeature.setMaximumSize(QtCore.QSize(300, 300))
        self.dockWidget = QtGui.QDockWidget(tlFormFeature)
        self.dockWidget.setEnabled(True)
        self.dockWidget.setGeometry(QtCore.QRect(0, 0, 300, 300))
        self.dockWidget.setMinimumSize(QtCore.QSize(300, 300))
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))

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

        self.retranslateUi(tlFormFeature)
        QtCore.QMetaObject.connectSlotsByName(tlFormFeature)

    def retranslateUi(self, tlFormFeature):
        pass

    def featureUpdated(self,tlayer,feat):
        try:
            self.symbol.setPixmap(ActiveLayerSymbolPixmap(self._layer,feat))
            self.dockWidget.setWindowTitle(feat['match'])
            feat['context'] = 'dock-content'
            payload = self._palyr.getLabelExpression().evaluate(feat)
#            self.payload.setText(payload)
#            self.name.setText(feat['name'])
        except Exception as e:
            Log.debug("TextFeatureDock - featureUpdated: " + str(e))
        pass


class tlTextFeatureDock(tlFeatureDock):

    def __init__(self, iface, tlayer, feature,show = True):
        super(tlTextFeatureDock,self).__init__(iface,tlayer,feature,show)

    def setupUi(self, tlTextFeature):
        tlTextFeature.setObjectName(_fromUtf8("tlTextFeature"))
        tlTextFeature.resize(300, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tlTextFeature.sizePolicy().hasHeightForWidth())
        tlTextFeature.setSizePolicy(sizePolicy)
        tlTextFeature.setMaximumSize(QtCore.QSize(300, 300))
        self.dockWidget = QtGui.QDockWidget(tlTextFeature)
        self.dockWidget.setEnabled(True)
        self.dockWidget.setGeometry(QtCore.QRect(0, 0, 300, 300))
        self.dockWidget.setMinimumSize(QtCore.QSize(300, 300))
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
        self.payload.setText(_translate("tlTextFeature", "Payload", None))

    def featureUpdated(self,tlayer,feat):
        try:
            self.symbol.setPixmap(ActiveLayerSymbolPixmap(self._layer,feat))
            self.dockWidget.setWindowTitle(feat['match'])
            feat['context'] = 'dock-content'
            payload = self._palyr.getLabelExpression().evaluate(feat)
            self.payload.setText(payload)
            self.name.setText(feat['name'])
        except Exception as e:
            Log.debug("TextFeatureDock - featureUpdated: " + str(e))
        pass

class tlSVGFeatureDock(tlFeatureDock):

    def __init__(self, iface, tlayer, feature,show = True):
        super(tlSVGFeatureDock,self).__init__(iface,tlayer,feature,show)

    def setupUi(self, tlSVGFeature):
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tlSVGFeature.sizePolicy().hasHeightForWidth())
        tlSVGFeature.setSizePolicy(sizePolicy)
        tlSVGFeature.setMaximumSize(QtCore.QSize(300, 300))
        self.dockWidget = QtGui.QDockWidget(tlSVGFeature)
        self.dockWidget.setEnabled(True)
        self.dockWidget.setGeometry(QtCore.QRect(0, 0, 300, 300))
        self.dockWidget.setMinimumSize(QtCore.QSize(300, 300))
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.svgWidget = QtSvg.QSvgWidget(self.dockWidgetContents)
        self.svgWidget.setGeometry(QtCore.QRect(0, 0, 300, 300))
        self.svgWidget.setObjectName(_fromUtf8("svgWidget"))
        self.dockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(tlSVGFeature)
        QtCore.QMetaObject.connectSlotsByName(tlSVGFeature)

    def retranslateUi(self, tlSVGFeature):
        pass


    def featureUpdated(self,tlayer,feat):
        try:
  #          self.symbol.setPixmap(ActiveLayerSymbolPixmap(self._layer,feat))
            self.dockWidget.setWindowTitle(feat['match'])
#            feat['context'] = 'dock-content'
 #           self.name.setText(feat['name'])
        except Exception as e:
            Log.debug("SVGFeatureDock - featureUpdated: " + str(e))
        pass







