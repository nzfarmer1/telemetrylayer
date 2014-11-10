# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tlFileTopicManager
 
 Topic Manager that supports an XML file format definition of topics
 
 See data/systopics.xml for example format

 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from TelemetryLayer.tlxmltopicparser import tlXMLTopicParser as XMLTopicParser
from TelemetryLayer.tltopicmanager import tlTopicManager as TopicManager
from TelemetryLayer.lib.tlsettings import tlSettings as Settings
from TelemetryLayer.lib.tllogging import tlLogging as Log

from ui_tlfiletopicmanager import Ui_tlFileTopicManager

import os


class tlFileTopicManager(TopicManager, Ui_tlFileTopicManager):
    def __init__(self, broker, create=False):
        super(tlFileTopicManager, self).__init__(broker, create)
        self._topics = []
        self._broker = broker
        self._create = create
        self._file_name = None


    def setupUi(self):
        super(tlFileTopicManager, self).setupUi()
        self.selectFileButton.clicked.connect(self._process)
        self.reloadFileButton.clicked.connect(self._reload)
        self.listTopicsTable.doubleClicked.connect(lambda: Log.openFileInBrowser(self._file_name))

        self.reloadFileButton.setEnabled(False)
        if self._create:
            self.reloadFileButton.setEnabled(False)
        else:
            self._file_name = Settings.get('XMLTopicFile-' + str(self._broker.id()))
            if self._file_name and os.path.exists(self._file_name):
                self.fileNameLabel.setText(os.path.basename(self._file_name))
                self._reload()


    def timerEvent(self):
        QObject.emit(self, QtCore.SIGNAL('topicManagerReady'), True, self)


    def getWidget(self):
        self.setupUi()
        QObject.emit(self, QtCore.SIGNAL('topicManagerReady'), True, self)
        return self.Tabs.widget(0)


    def getTopics(self):
        return super(tlFileTopicManager, self).getTopics(self._topics)  # Merge System topics


    def setLabelFormatter(self, layer, topicType):
        Log.debug("setFormatter")
        palyr = QgsPalLayerSettings()
        palyr.readFromLayer(layer)
        palyr.enabled = True
        palyr.placement = QgsPalLayerSettings.OverPoint
        palyr.quadOffset = QgsPalLayerSettings.QuadrantBelow
        palyr.yOffset = 0.01
        palyr.fieldName = '$format_label'
        palyr.writeToLayer(layer)

    def setLayerStyle(self, layer, topicType):
        if not self.path() in QgsApplication.svgPaths():
            QgsApplication.setDefaultSvgPaths(QgsApplication.svgPaths() + [self.path()])
        self.loadStyle(layer, os.path.join(self.path(), "rules.qml"))


    def _process(self):
        file_name = QtGui.QFileDialog.getOpenFileName(self, 'Select XML File', "", "XML topic file (*.xml)")
        if file_name:
            self._file_name = file_name
            self._topics = XMLTopicParser(self._file_name).getTopics()
            self._listTopics()
            Settings.set('XMLTopicFile-' + str(self._broker.id()), self._file_name)
            self.reloadFileButton.setEnabled(True)

    def _reload(self):
        if self._file_name and os.path.exists(self._file_name):
            self._topics = XMLTopicParser(self._file_name).getTopics()
            self._listTopics()
            self.reloadFileButton.setEnabled(True)
        else:
            Log.info("There was a problem loading " + self._file_name)


    def _listTopics(self):

        tbl = self.listTopicsTable
        columns = ["Name", "Type", "Topic"]
        tbl.clear()
        tbl.setRowCount(0)
        tbl.setStyleSheet("font: 10pt \"System\";")
        tbl.setColumnCount(len(columns))
        tbl.setHorizontalHeaderLabels(columns)
        tbl.verticalHeader().setVisible(True)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)

        row = 0

        for topic in self._topics:
            tbl.setRowCount(row + 1)
            item = QtGui.QLabel(topic['name'])
            item.setToolTip(topic['desc'])
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 0, item)

            tbl.setRowCount(row + 1)
            item = QtGui.QLabel(topic['type'])
            item.setToolTip(topic['desc'])
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 1, item)
            tbl.setRowCount(row + 1)

            item = QtGui.QLabel(topic['topic'])
            item.setToolTip(topic['desc'])
            item.setStyleSheet("padding: 4px")
            tbl.setCellWidget(row, 2, item)
            row += 1

        tbl.resizeColumnsToContents()
        # tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        tbl.horizontalHeader().setStretchLastSection(True)
