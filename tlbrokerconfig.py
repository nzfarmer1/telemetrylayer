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

from forms.ui_tlbrokerconfig import Ui_tlBrokerConfig
from tlbrokers import tlBrokers as Brokers
from lib.tlsettings import tlSettings as Settings
from lib.tlsettings import tlConstants as Constants
from lib.tllogging import tlLogging as Log
from tlmqttclient import *
import traceback, sys, os, imp, json, zlib
import copy, pickle


# Todo
# Add Help Button


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



class tlBrokerConfig(QtGui.QDialog, Ui_tlBrokerConfig):
    """
    Class to manage the addition/deletion/configuration of Brokers
    Supports loading of dyanmic Topic Manager
    """

    kBrokerConfigTabId = 0
    kFeatureListTabId = 1
    kTopicManagerTabId = 2
    kLayerId = 0
    kFeatureId = 1
    kFeature = 3
    kDataCol = 0
    kLayerNameCol = 1
    kFeatureNameCol = 2
    kPayloadCol = 3

    def __init__(self, creator, broker, create=False):
        super(tlBrokerConfig, self).__init__()

        self._creator = creator
        self.plugin_dir = creator.plugin_dir
        self._iface = creator.iface
        self._layerManager = creator._layerManager
        self._create = create
        self._broker = broker
        self._tested = False
        self._fd = None

        if self._create:
            self._mode = Constants.Create
        else:
            self._mode = Constants.Update

        self.setupUi()


    def setupUi(self):
        super(tlBrokerConfig, self).setupUi(self)

        self.connectHelp.clicked.connect(self._help)
        self.connectTest.clicked.connect(self._test)

        self.connectName.setValidator(QRegExpValidator(QRegExp("^[a-zA-Z0-9\s]+"), self))
        self.connectHost.setValidator(QRegExpValidator(QRegExp("^[a-z0-9\-\.]+"), self))
        self.connectHostAlt.setValidator(QRegExpValidator(QRegExp("^[a-z0-9\-\.]+"), self))

        
        self.Tabs.setCurrentIndex(self.kBrokerConfigTabId)  # First index
        


        # if Modal create mode
        self.setName(self._broker.name())
        self.setHost(self._broker.host())
        self.setPort(str(self._broker.port()))

        self.setHostAlt(self._broker.hostAlt())
        self.setPortAlt(str(self._broker.portAlt()))

        self.setPoll(str(self._broker.poll()))
        self.setKeepAlive(str(self._broker.keepAlive()))

        self.setUsername(self._broker.username())   
        self.setPassword(self._broker.password())

        self._connectedTLayers = []
        self._featureListItems = {}
        self._refreshFeature = QTimer()
        self._refreshFeature.setSingleShot(True)
        self._refreshFeature.timeout.connect(self._updateFeatureList)
        self.Tabs.currentChanged.connect(lambda: self._refreshFeature.start(3))
        QgsMapLayerRegistry.instance().layersRemoved.connect(self._updateFeatureList)
        QgsProject.instance().layerLoaded.connect(self._updateFeatureList)
        
        self.tableFeatureList.doubleClicked.connect(self._showFeatureDialog)
        self.tableFeatureList.clicked.connect(self._zoomToFeature)

        self.connectApply.setEnabled(False)


        if self._mode == Constants.Create:  # Create Layer - so Modal
            self.connectPoll.setCurrentIndex(
                self.connectPoll.findText(Settings.get('mqttPoll', 5)))
            self.connectApply.setText(_translate("tlBrokerConfig", "Create", None))
            self.connectApply.clicked.connect(self.accept)
            self.dockWidget.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
            self.dockWidget.setWindowTitle(_translate("tlBrokerConfig", "Add Broker", None))
            #self.Tabs.setEnabled(False)
            #   self.connectFarmSenseServer.setEnabled(False)
        elif self._mode == Constants.Update:
            
            if self._broker.useAltConnect():
                self.connectDefault.setChecked(False)
                self.connectAlt.setChecked(True)
            else:
                self.connectDefault.setChecked(True)
                self.connectAlt.setChecked(False)

            self.dockWidget.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
            self.dockWidget.setWindowTitle(_translate("tlBrokerConfig", "Configure ", None) + self.getName())
            self.connectApply.setText(_translate("tlBrokerConfig", "Apply", None))
            self.dockWidget.visibilityChanged.connect(self.tearDown)


        self.connectName.textChanged.connect(lambda: self.setDirty(True))
        self.connectHost.textChanged.connect(lambda: self.setDirty(True))
        self.connectPort.textChanged.connect(lambda: self.setDirty(True))
        self.connectHostAlt.textChanged.connect(lambda: self.setDirty(True))
        self.connectPortAlt.textChanged.connect(lambda: self.setDirty(True))
        self.connectUsername.textChanged.connect(lambda: self.setDirty(True))
        self.connectPassword.textChanged.connect(lambda: self.setDirty(True))
        self.connectPoll.currentIndexChanged.connect(lambda: self.setDirty(True))
        self.connectKeepAlive.currentIndexChanged.connect(lambda: self.setDirty(True))
        self.connectAlt.toggled.connect(lambda: self.setDirty(True))
        self.connectDefault.toggled.connect(lambda: self.setDirty(True))

    def mode(self):
        return self._mode


    def _updateFeatureList(self, fid=None):
        if self.dockWidget.isVisible() and self.Tabs.currentIndex() == self.kFeatureListTabId:
            self._loadFeatureList()
        pass


    def _zoomToFeature(self, modelIdx):
        item = self.tableFeatureList.item(modelIdx.row(), 0)
        layer = QgsMapLayerRegistry.instance().mapLayer(item.data(self.kLayerId))  #
        request = QgsFeatureRequest(item.data(self.kFeatureId))
        feature = next(layer.getFeatures(request), None)
        modifiers = QtGui.QApplication.keyboardModifiers()
        self._iface.legendInterface().setCurrentLayer(layer)
        if modifiers == QtCore.Qt.ShiftModifier:
            selectList = [feature.id()]
            if not feature['visible'] and not layer.isReadOnly():
                layer.startEditing()
                layer.changeAttributeValue(feature.id(), Constants.visibleIdx, True)
                layer.commitChanges()
            layer.setSelectedFeatures(selectList)
            box = layer.boundingBoxOfSelected()
            self._iface.mapCanvas().setExtent(box)
            self._iface.mapCanvas().refresh()
        pass



    def _showFeatureDialog(self, modelIdx):
        item = self.tableFeatureList.item(modelIdx.row(), self.kDataCol)
        layer = QgsMapLayerRegistry.instance().mapLayer(item.data(self.kLayerId))
        modifiers = QtGui.QApplication.keyboardModifiers()
         
            

        try:
            if layer.isEditable() or modifiers == QtCore.Qt.ControlModifier:
                self._creator.showEditFeature(layer,item.data(self.kFeatureId))
                #self._iface.openFeatureForm(layer, feature, True,False)
            else:
                feature = next(layer.getFeatures(QgsFeatureRequest(item.data(self.kFeatureId))), None)
                self._layerManager.showFeatureDock(layer,
                                                feature)
#            self._fd = tlFeatureDialogWrapper(self._iface,
#                                                 self._layerManager.getTLayer(layer.id()),
#                                                 feature)
                                                 

        except Exception as e:
            Log.debug(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type, exc_value,
                                             exc_traceback)))
            pass

    def _closedFeatureDialog(self, tLayer):
        tLayer.layer().commitChanges()
        self._updateFeatureList()

    # Show a list of features for the layers associated with this broker            
    def _loadFeatureList(self):

        self._featureListItems = {}
        tbl = self.tableFeatureList

        columns = ["Data", "Layer", "Feature", "Last"]
        createMode = tbl.rowCount() == 0
        selectedRow =None
        if tbl.rowCount() >0:
            for item in tbl.selectedRanges():
                 selectedRow = item
        tbl.clear()
        tbl.setRowCount(0)
        tbl.setStyleSheet("font: 10pt \"System\";")
        tbl.setColumnCount(len(columns))
        tbl.setHorizontalHeaderLabels(columns)
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)

        lm = self._layerManager
        if lm is None:
            return


        _palyr = QgsPalLayerSettings()
        row = 0
        for lid, tLayer in self._layerManager.getTLayers().iteritems():
            _palyr.readFromLayer(tLayer.layer())

            if tLayer.getBroker().id() != self._broker.id():
                continue

            if not tLayer in self._connectedTLayers:
                # Add connections and append to connected layers

                tLayer.featureUpdated.connect(self._updateFeatureList)
                tLayer.layer().featureAdded.connect(self._updateFeatureList)
                tLayer.layer().featureDeleted.connect(self._updateFeatureList)

                self._connectedTLayers.append(tLayer)

            features = tLayer.layer().getFeatures()
            tooltip = "Double click to see feature; Shift-click to view on layer; Command-click to edit the feature"
            for feat in features:

                if feat.id() <= 0:
                    continue

                feature =   QgsFeature(feat)
                feature['context'] = 'feature-list' # replace with constants

                tbl.setRowCount(row + 1)
                # Append the feature
                self._featureListItems[(lid, feature.id())] = row
                item = QTableWidgetItem()
                item.setData(self.kLayerId, lid)
                item.setData(self.kFeatureId, feature.id())
                item.setData(self.kFeature, feature)

                tbl.setItem(row, self.kDataCol, item)

                item = QtGui.QLabel(tLayer.layer().name())
                item.setToolTip(tooltip)
                item.setStyleSheet("padding: 4px")
                tbl.setCellWidget(row, self.kLayerNameCol, item)

                item = QtGui.QLabel(feature['name'])
                item.setToolTip(tooltip)
                item.setStyleSheet("padding: 4px")
                tbl.setCellWidget(row, self.kFeatureNameCol, item)

                item = QtGui.QLabel(_palyr.getLabelExpression().evaluate(feature))
                item.setToolTip(tooltip)
                item.setStyleSheet("padding: 4px")
                tbl.setCellWidget(row, self.kPayloadCol, item)
                
                if selectedRow and selectedRow.topRow() == row:
                    tbl.setRangeSelected(selectedRow,True)
                    selectedRow =None

                row += 1

        tbl.setColumnHidden(0, True)
        tbl.resizeColumnsToContents()
        tbl.horizontalHeader().setStretchLastSection(True)


    """ Setters """


    def setDirty(self,state):
        self._broker.setDirty(state)
        self.connectApply.setEnabled(self.connectApply.isEnabled() or state)

    def setName(self, name):
        self.connectName.setText(name)

    def setHost(self, host):
        self.connectHost.setText(host)

    def setHostAlt(self, host):
        self.connectHostAlt.setText(host)

    def setPort(self, port =1883):
        self.connectPort.setText(str(port))

    def setPortAlt(self, port = 1883):
        if port.isdigit():
            self.connectPortAlt.setText(str(port))
        else:
            self.connectPortAlt.setText(str(1883))

    def setUsername(self, username):
        self.connectUsername.setText(username)

    def setPassword(self, password):
        self.connectPassword.setText(password)

    def setKeepAlive(self, keepalive):
        idx = self.connectKeepAlive.findText(str(keepalive))
        if idx is None:
            idx = 0
        self.connectKeepAlive.setCurrentIndex(idx)

    def setPoll(self, interval):
        if int(interval) < 1000:
            interval = 1000 # Min 1 second
        _interval = int(float(1.0 / 1000) * float(interval))
        self.connectPoll.setCurrentIndex(self.connectPoll.findText(str(_interval)))

    def setTested(self, state=True):
        self._tested = state

    """ Getters """


    def getHost(self):
        return self.connectHost.text()

    def getHostAlt(self):
        return self.connectHostAlt.text()

    def getPort(self):
        if len(self.connectPort.text()) > 0:
            return int(self.connectPort.text())
        return None

    def getPortAlt(self):
        if len(self.connectPortAlt.text()) > 0:
            return int(self.connectPortAlt.text())
        return None

    def getUsername(self):
        return self.connectUsername.text()

    def getPassword(self):
        return self.connectPassword.text()

    def getPoll(self):
        return int(self.connectPoll.itemText(self.connectPoll.currentIndex())) * 1000

    def getUseAltConnect(self):
        return self.connectAlt.isChecked()

    def getKeepAlive(self, default="0"):
        val = self.connectKeepAlive.itemText(self.connectKeepAlive.currentIndex())
        if val is None or not val.isdigit():
            val = default
        return int(val)

    def getTested(self):
        return self._tested

    def dirty(self):
        if not self.dockWidget.isVisible():
            return self._broker.dirty()

        dirty = False
        dirty = dirty or self._broker.name() != self.getName()
        dirty = dirty or self._broker.host() != self.getHost()
        dirty = dirty or self._broker.port() != self.getPort()
        dirty = dirty or self._broker.username() != self.getUsername()
        dirty = dirty or self._broker.password() != self.getPassword()
        dirty = dirty or self._broker.hostAlt() != self.getHostAlt()
        dirty = dirty or self._broker.portAlt() != self.getPortAlt()
        dirty = dirty or self._broker.useAltConnect() != self.getUseAltConnect()
        dirty = dirty or self._broker.poll() != self.getPoll()
        dirty = dirty or self._broker.keepAlive() != self.getKeepAlive()

        return dirty or self._broker.dirty()


    def getName(self):
        return self.connectName.text()

    def getBroker(self):
        self._broker.setName(self.getName())
        self._broker.setHost(self.getHost())
        self._broker.setPort(self.getPort())
        self._broker.setUsername(self.getUsername())
        self._broker.setPassword(self.getPassword())
        self._broker.setHostAlt(self.getHostAlt())
        self._broker.setPortAlt(self.getPortAlt())
        self._broker.setUseAltConnect(self.getUseAltConnect())
        self._broker.setPoll(self.getPoll())
        self._broker.setKeepAlive(self.getKeepAlive())
        return self._broker

    
    """ Validator """


    def validate(self):
        if len(self.getName()) == 0:
            Log.alert("Please supply a name for this broker")
            return False


        if not Brokers.instance().uniqName(self._broker.id(), self.getName()):
            Log.alert("A broker named " + self.getName() + " already exists")
            return False
        

        if len(self.getHost()) == 0:
            Log.alert("Please supply a hostname")
            return False

        if self.getUseAltConnect() and len(self.getHostAlt()) == 0:
            Log.alert("Please supply a hostname (alt)")
            return False

        if self.getPort() is None:
            Log.alert("Please specify a port")
            return False

        if self.getUseAltConnect() and self.getPortAlt() is None:
            Log.alert("Please supply a port (alt)")
            return False

        return True


    def _test(self):
        if not self.validate():
            return

        Log.progressPush("Testing Connection")
        #QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.connectTest.setEnabled(False)

        _client = tlMqttSingleShot(self,
                                self.getBroker(),
                                None,
                                ["#"],
                                None,
                                0, #qos
                                self._on_test)
        # change to simple connection test?
        _client.mqttOnConnect.connect(lambda:self._on_test(_client,True))
#        QObject.connect(_client, SIGNAL("mqttOnConnect"), lambda:self._on_test(_client,True))
  
#        _client.mqttOnConnect.connect(lambda:self._on_test(_client,True))
        _client.run()

    
    def _on_test(self, client, status = True, msg = None):
        if self.connectTest.isEnabled():
            return # ignore duplicate responses
        
        self.connectTest.setEnabled(True)
        self.setTested(status)
        
        Log.progressPop("Testing Connection")
        if not status:
            Log.alert("Connection test failed\n\n" + str(msg))
        else:
            Log.alert("MQTT Connection successful")
            
        client.kill();



    def _help(self):
        webbrowser.open(Settings.getMeta('helpURL'))

    def _showLog(self, state):
        logDock = self._iface.mainWindow().findChild(QtGui.QDockWidget, 'MessageLog')
        if state:
            logDock.show()
        else:
            logDock.hide()


    def accept(self):
        self.connectHelp.clicked.disconnect(self._help)
        self.connectTest.clicked.disconnect(self._test)
        super(tlBrokerConfig, self).accept()


    def tearDown(self):
        if not self.dockWidget.isVisible():
            if self._mode != Constants.Update:
                return
            self._refreshFeature.timeout.disconnect(self._updateFeatureList)
            # for tLayer in self._connectedTLayers:
            # Delete connections
            #       tLayer.layer().featureAdded.disconnect(self._updateFeatureList)
            #       tLayer.layer().featureDeleted.disconnect(self._updateFeatureList)

            self._connectedTLayers = []
            
            QgsMapLayerRegistry.instance().layersRemoved.disconnect(self._updateFeatureList)
            QgsProject.instance().layerLoaded.disconnect(self._updateFeatureList)
            if  self.tableFeatureList.isVisible():
                self.tableFeatureList.doubleClicked.disconnect(self._showFeatureDialog)
                self.tableFeatureList.clicked.disconnect(self._zoomToFeature)


    
