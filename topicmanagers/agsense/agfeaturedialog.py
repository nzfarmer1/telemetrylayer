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

from agdevice import agDeviceList, agDevice, agParams, agParam
from ui_agdatatabwidget import Ui_Form
import os, zlib, datetime, json, numpy


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



class agFeatureDialog(tlFeatureDialog):
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

        super(agFeatureDialog, self).__init__(dialog, tLayer, feature, widgets)

        topicCombo = self._find(QComboBox, 'topic') # Disable changing topics!
        Log.debug(topicCombo);
        if not topicCombo is None:
             Log.debug("Setting disabled")
             Log.debug(topicCombo.isEnabled())
             topicCombo.setEnabled(False)
             Log.debug(topicCombo.isEnabled())

        

    