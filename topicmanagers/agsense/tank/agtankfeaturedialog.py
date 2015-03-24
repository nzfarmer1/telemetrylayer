# -*- coding: utf-8 -*-
"""
/***************************************************************************
 dsFeatureDialog
 
 Charting and Data panels of the custom feature dialog

 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from TelemetryLayer.tltopicmanager import tlTopicManager, tlFeatureDialog
from TelemetryLayer.lib.tlsettings import tlSettings as Settings, tlConstants as Constants
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tlmqttclient import *
from TelemetryLayer.tlbrokers import tlBrokers as Brokers

from TelemetryLayer.topicmanagers.agsense.agutils import *

from TelemetryLayer.topicmanagers.agsense.agdevice import agDeviceList, agDevice, agParams, agParam
from TelemetryLayer.topicmanagers.agsense.ui_agdatatabwidget import Ui_Form

import os, zlib, datetime, json, numpy,traceback,sys



class agDataTab(QDialog, Ui_Form):
    def __init__(self):
        Log.debug("Init form")
        try:
            super(agDataTab, self).__init__()
            self.setupUi(self)
        except Exception as e:
            Log.debug(e)


class agDataView(QObject):
    def __init__(self, tLayer, feature):
        super(agDataView, self).__init__()

    def _request(self, interval, duration):
        pass

    def _update(self, client, status, msg):
        pass

class agDataLoggerView(agDataView):
    def __init__(self, tabs, tLayer, feature):
        super(agDataLoggerView, self).__init__(tLayer, feature)
        pass

    def _export(self):
        pass

    def _intervalChanged(self, idx):
        pass

    def show(self):
        pass

    def _refresh(self):
        pass
    
    def _error(self, mqtt, msg=""):
        Log.warn(msg)

    def update(self, data):
        pass

class agChartView(agDataView):
    def __init__(self, tabs, tLayer, feature):
        super(dsChartView, self).__init__(tLayer, feature)
        self._tabs = tabs
        # self._tabs.btnRefreshc.setEnabled(True)


    def _intervalChanged(self, idx):
        pass

    def show(self):
        pass

    def update(self, data):
        pass

    def _refresh(self):
        pass

    def _error(self, mqtt, msg=""):
        pass




class agTankFeatureDialog(tlFeatureDialog):
    """
    Implementation of tlFeatureDialog.

    """

    @staticmethod
    def _createTab(Tabs, widget):
        idx = Tabs.indexOf(widget)
        return Tabs.widget(idx), Tabs.tabText(idx), idx

    def __init__(self, dialog, tLayer, feature):
        agTabs = agDataTab()
        widgets = []
        Tabs = agTabs.Tabs

        try:
            topic = tLayer.getBroker().topic(feature['topic'])
            params = topic['params']

        except KeyError: 
            super(agTankFeatureDialog, self).__init__(dialog, tLayer, feature, widgets)
            return
            pass
        
        #widgets.append(tlDsFeatureDialog._createTab(Tabs, dsTabs.dataTab))
        #widgets.append(tlDsFeatureDialog._createTab(Tabs, dsTabs.chartTab))

        if len(params) >0:
            widgets.append(agTankFeatureDialog._createTab(Tabs, agTabs.configTab))

        super(agTankFeatureDialog, self).__init__(dialog, tLayer, feature, widgets)
        if len(params) >0:
            self._configTab = agConfigView(agTabs, tLayer, feature)
            self._configTab.show()

        topicCombo = self._find(QComboBox, 'topic') # Disable changing topics!
        if topicCombo:
            topicCombo.setEnabled(False)
        

    