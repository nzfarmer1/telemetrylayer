# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlBrokerConfig
 
 Configure individual Brokers
 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import webbrowser,pickle,json

from lib.tlsettings import tlSettings as Settings
from lib.tlsettings import tlConstants as Constants
from lib.tllogging import tlLogging as Log
from forms.ui_tleditfeature import Ui_tlEditFeature

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


class tlFeatureDock(QDialog,Ui_tlEditFeature):
    """
    Dialog to manage a feature within a dock
    """

    def __init__(self, iface, tlayer, feature):
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
        self._images = {}
       
        self.dockWidget.resizeEvent = self._dockLocationChanged       
        self.dockWidget.show()
        #self.payload.setStyleSheet('font-size: 72pt; font-family: Arial;')
        
#        font = QFont()
 #       font.setPointSize(200);
  #      font.setBold(True);
   #     self.payload.setFont(font)
        self.payload.setAutoFillBackground(True)
        
        self._featureUpdated(self._tlayer,feature)
        pass
    
    
    def _featureUpdated(self,tlayer,feat):
        try:
            if not self.isVisible():
                return

            if feat.id() != self._feature.id():
                return
    
            r =  self._tlayer.layer().rendererV2()
            items = r.legendSymbologyItems(QSize(32,32))
            pos = map(lambda(rule):
                rule.isFilterOK(feat), r.rootRule().children()).index(True,0)
            (state,pixmap) = items[pos]
            if not self._images.has_key(state):
                symbol  = r.rootRule().children()[pos].symbol().clone()
                symbol.setSize(50.0)
                symbol.symbolLayer(0).setVerticalAnchorPoint(QgsMarkerSymbolLayerV2.VCenter)
                symbol.symbolLayer(0).setHorizontalAnchorPoint(QgsMarkerSymbolLayerV2.HCenter)
                image = symbol.bigSymbolPreviewImage()
                self._images[state] = QPixmap.fromImage(image)
            
            self.symbol.setPixmap(self._images[state])
            feat['context'] = 'dock-title'
            title = feat['name'] + ' - ' + self._palyr.getLabelExpression().evaluate(feat)
            
            self.dockWidget.setWindowTitle(title)
            
            feat['context'] = 'dock-content'
            payload = self._palyr.getLabelExpression().evaluate(feat)
            self.payload.setText(payload)
        except Exception as e:
            Log.debug("FeatureDock " + str(e))
        pass

    
    def saveGeometry(self):
            Settings.setp(self._key,pickle.dumps(self.dockWidget.saveGeometry()))
    
    def restoreGeometry(self):
            geometry = pickle.loads(Settings.getp(self._key,pickle.dumps(None)))
            if geometry is None:
                return
            self.dockWidget.restoreGeometry(geometry)

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
        Log.debug("Visibility changed " + str(self.isVisible()))
        Log.debug("Focus" + str(self.dockWidget.hasFocus()))
        Log.debug(self.frameSize())
        Log.debug(self.dockWidget.frameSize())
        if not visible:
            self.saveGeometry()
        else:
            self.restoreGeometry()
        pass
    
    def _resizeFeatureDialog(self):
        pass

    def _accepted(self):
        Log.debug("Accepted")

