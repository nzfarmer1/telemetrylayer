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
import webbrowser

from lib.tlsettings import tlSettings as Settings
from lib.tlsettings import tlConstants as Constants
from lib.tllogging import tlLogging as Log
#from tlmqttclient import *
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
        
        super(tlFeatureDock,self).__init__()
        self.setupUi(self)
        self.dockWidget.setWindowTitle(feature['name'])
        self.dockWidget.setAllowedAreas(Qt.AllDockWidgetAreas)
        self._iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
        self.dockWidget.hide()
        self.dockWidget.setFloating(True)
        self.dockWidget.resize(300,300)
        self.dockWidget.move(300,300)
        self.dockWidget.show()
        self.dockWidget.setObjectName(str(self))
        self._palyr = QgsPalLayerSettings()
        self._palyr.readFromLayer(tlayer.layer())
        self._tlayer.featureUpdated.connect(self._featureUpdated)
        self._featureUpdated(self._tlayer,feature)
        Log.debug(self.dockWidget.saveGeometry())
        pass
    
 #   def closeEvent(event):
#        Log.debug(saveGeometry())

    def isVisible(self):
        return self.dockWidget.isVisible()
    
    def _featureUpdated(self,tLayer,feat):
        try:
            if feat.id() != self._feature.id():
                return
    
            r =  self._tlayer.layer().rendererV2()
            items = r.legendSymbologyItems(QSize(32,32))
            pos = map(lambda(rule):
                rule.isFilterOK(feat), r.rootRule().children()).index(True,0)
            (state,pixmap) = items[pos]
            symbol  = r.rootRule().children()[pos].symbol().clone()
            symbol.setSize(50.0)
            symbol.symbolLayer(0).setVerticalAnchorPoint(QgsMarkerSymbolLayerV2.VCenter)
            symbol.symbolLayer(0).setHorizontalAnchorPoint(QgsMarkerSymbolLayerV2.HCenter)
            image = symbol.bigSymbolPreviewImage()
            
            self.dockWidget.setWindowTitle(feat['name'] + ' - ' + state)
            self.symbol.setPixmap(QPixmap.fromImage(image) )
            self.payload.setText(self._palyr.getLabelExpression().evaluate(feat))
        except Exception as e:
            Log.debug("FeatureDock " + str(e))
        pass
    
    
    def _resizeFeatureDialog(self):
        pass

    def _validateApply(self):
        self.accept()

