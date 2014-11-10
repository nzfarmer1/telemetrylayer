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

from ui_dsdatatabwidget import Ui_Form
from dsdevicemapdialog import DeviceMap, DeviceMaps, DeviceType, DeviceTypes, dsParameterTable as ParameterTable

from dsrpcproxy import dsRPCProxy as RPCProxy

import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter, HourLocator, MinuteLocator, SecondLocator
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


class dsDataTab(QDialog, Ui_Form):
    def __init__(self):
        Log.debug("Init form")
        try:
            super(dsDataTab, self).__init__()
            self.setupUi(self)
        except Exception as e:
            Log.debug(e)


class dsDataView(QObject):
    def __init__(self, tLayer, feature):
        super(dsDataView, self).__init__()
        self._tlayer = tLayer
        self._feature = feature
        self._client = None
        pass

    @staticmethod
    def _intervals():
        return [['Tick', [(1, 3600, '1 Hour'), (1, 7200, '2 Hours'), (1, 10600, '3 Hours'), (1, 14400, '4 Hours'),
                          (1, 18000, '5 Hours'), (1, 21600, '6 Hours'), (1, 43200, '12 Hours'),
                          (1, 86400, '24 Hours')]],
                ['1 Minute', [(60, 1440, '1 Day'), (60, 2880, '2 Days'), (60, 7200, '5 Days'), (60, 14400, '10 Days')]],
                ['15 Minutes', [(900, 960, '10 Days')]]]

    def _request(self, interval, duration):
        publish = "/digisense/request/data/" + str(interval * duration) + "/" + str(interval)
        try:
            self._client = tlMqttSingleShot(self,
                                            self._tlayer.host(),
                                            self._tlayer.port(),
                                            # "/digisense/request/data/10000/1",
                                            publish,
                                            ["/digisense/response/data" + self._feature['topic'],
                                             "/digisense/response/data" + self._feature['topic'] + "/compressed"],
                                            self._feature['topic'],
                                            30)
            QObject.connect(self._client, QtCore.SIGNAL("mqttOnCompletion"), self._update)
            QObject.connect(self._client, QtCore.SIGNAL("mqttConnectionError"), self._error)
            QObject.connect(self._client, QtCore.SIGNAL("mqttOnTimeout"), self._error)

            Log.progress("Requesting data for " + str(self._feature['topic']))
            self._client.run()
        except Exception:
            Log.debug("Data Logger ")
            self._client.kill()

    def _update(self, client, status, msg):
        if not status:
            Log.alert(msg)
            return
        if 'compressed' in msg.topic:
            response = json.loads(zlib.decompress(msg.payload))
        else:
            response = json.loads(msg.payload)

        if 'warn' in response and 'warning' in response:
            Log.progress(response['warning'])

        records = response['records']
        if records < 1:
            Log.progress("Nothing returned")
            data = []
        else:
            data = response['data']

        self.update(data)


class dsDataLoggerView(dsDataView):
    def __init__(self, tabs, tLayer, feature):
        super(dsDataLoggerView, self).__init__(tLayer, feature)
        self._tabs = tabs
        self._dataTable = tabs.tableWidget

        for (name, durations) in self._intervals():
            self._tabs.selectInterval.addItem(name, durations)
            if name == 'Tick':
                for (interval, duration, name) in durations:
                    self._tabs.selectDuration.addItem(name, (interval, duration))

        self._tabs.btnRefresh.clicked.connect(self._refresh)
        self._tabs.btnExport.clicked.connect(self._export)
        self._tabs.selectInterval.currentIndexChanged.connect(self._intervalChanged)

    def _export(self):
        fileName = QFileDialog.getSaveFileName(None, "Location for export (.csv) File",
                                               "~/",
                                               "*.csv")
        if not fileName:
            return
        try:
            qfile = QFile(fileName)
            qfile.open(QIODevice.WriteOnly)
            for row in self._dataTable.rowCount():
                x = self._dataTable.item(row, 0).text()
                y = self._dataTable.item(row, 1).text()
                QTextStream(qfile) << str(x) + "," + str(y) + "\n"
            qfile.flush()
            qfile.close()
        except Exception as e:
            Log.alert(str(e))


    def _intervalChanged(self, idx):
        durations = self._tabs.selectInterval.itemData(idx)
        self._tabs.selectDuration.clear()
        for (interval, duration, name) in durations:
            self._tabs.selectDuration.addItem(name, (interval, duration))

    def show(self):
        self._tabs.btnExport.setEnabled(False)
        columns = ["Time", "Value"]
        tbl = self._dataTable
        tbl.clear()

        tbl.setStyleSheet("font: 10pt \"System\";")
        tbl.setRowCount(0)
        tbl.setColumnCount(len(columns))
        tbl.setColumnWidth(30, 30)  # ?
        tbl.setHorizontalHeaderLabels(columns)
        # tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setVisible(True)
        tbl.setShowGrid(True)
        tbl.setSortingEnabled(True)

        tbl.resizeColumnsToContents()
        tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        pass

    def _refresh(self):
        (interval, duration) = self._tabs.selectDuration.itemData(self._tabs.selectDuration.currentIndex())
        self._request(interval, duration)
        self._tabs.btnRefresh.setEnabled(False)

    def _error(self, mqtt, msg=""):
        self._tabs.btnRefresh.setEnabled(True)
        Log.warn(msg)

    def update(self, data):

        tbl = self._dataTable
        try:
            tbl.setRowCount(0)

            row = 0
            for (x, y) in list(data):
                Log.debug(x)
                d = datetime.datetime.fromtimestamp(float(x))

                tbl.setRowCount(row + 1)
                item = QtGui.QTableWidgetItem(0)
                item.setText(d.strftime("%Y-%m-%d %H:%M:%S"))
                item.setFlags(Qt.NoItemFlags)
                tbl.setItem(row, 0, item)

                item = QtGui.QTableWidgetItem(0)
                # item.setText(d.strftime("%y-%m-%d-%H:%M:%S"))
                item.setText(str(y))
                item.setFlags(Qt.NoItemFlags)
                tbl.setItem(row, 1, item)

                row += 1
            tbl.resizeColumnsToContents()
            tbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        except Exception as e:
            Log.debug(e)
        finally:
            self._tabs.btnRefresh.setEnabled(True)
            self._tabs.btnExport.setEnabled(tbl.rowCount() > 0)


class dsChartView(dsDataView):
    @staticmethod
    def smoothListGaussian(dlist, degree=5):
        window = degree * 2 - 1
        weight = numpy.array([1. / numpy.exp(16. * i * i / window / window) for i in numpy.arange(-degree + 1, degree)])
        extended = numpy.r_[[dlist[0]] * (degree - 1), dlist, [dlist[-1]] * degree]
        smoothed = numpy.convolve(weight / weight.sum(), extended, mode='same')
        return smoothed[degree - 1:-degree]


    def __init__(self, tabs, tLayer, feature):
        super(dsChartView, self).__init__(tLayer, feature)
        self._tabs = tabs
        # self._tabs.btnRefreshc.setEnabled(True)

        for (name, durations) in self._intervals():
            self._tabs.selectIntervalc.addItem(name, durations)
            if name == 'Tick':
                for (interval, duration, name) in durations:
                    self._tabs.selectDurationc.addItem(name, (interval, duration))

        self._tabs.btnRefreshc.clicked.connect(self._refresh)
        self._tabs.selectIntervalc.currentIndexChanged.connect(self._intervalChanged)


    def _intervalChanged(self, idx):
        durations = self._tabs.selectIntervalc.itemData(idx)
        self._tabs.selectDurationc.clear()
        for (interval, duration, name) in durations:
            self._tabs.selectDurationc.addItem(name, (interval, duration))

    def show(self):
        pass

    def update(self, data):

        hours = HourLocator()  # every hour
        minutes = MinuteLocator(byminute=filter(lambda x: x % 20 == 0, range(60)))  # every minute
        seconds = SecondLocator()  # every second
        hoursFmt = DateFormatter('')
        data.reverse()
        x = map(lambda (x, y): datetime.datetime.fromtimestamp(float(x)), list(data))
        y = map(lambda (x, y): float(y), list(data))
        if True:  # smoothed
            y = self.smoothListGaussian(y)
        print y
        dpi = 72
        # plt.xlabel('', fontsize=10, color='grey')


        fig, ax = plt.subplots(figsize=(400 / dpi, 200 / dpi), dpi=dpi, )
        ax.plot_date(x, y, '-')

        #        plt.setp(ax, 'color', 'r', 'linewidth',1.0)

        # format the ticks
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(hoursFmt)
        ax.xaxis.set_minor_locator(minutes)
        ax.xaxis.set_minor_formatter(DateFormatter("%R"))
        ax.autoscale_view()
        ax.yaxis.tick_right()


        # format the coords message box
        def adc(x):
            return '%d' % x

        ax.fmt_xdata = DateFormatter('%H %i %s')
        ax.fmt_ydata = y
        ax.grid(True)
        fig.autofmt_xdate()

        byteArray = QByteArray()
        buff = QBuffer(byteArray)
        buff.open(QIODevice.WriteOnly)

        plt.xticks(rotation=30)

        plt.savefig(buff, format="png")
        buff.close()
        pxmap = QPixmap()
        if pxmap.loadFromData(byteArray, format="png"):
            scene = QGraphicsScene()
            scene.addPixmap(pxmap)
            self._tabs.graphicsView.setScene(scene)

        self._tabs.btnRefreshc.setEnabled(True)


    def _refresh(self):
        (interval, duration) = self._tabs.selectDurationc.itemData(self._tabs.selectDurationc.currentIndex())
        self._request(interval, duration)
        self._tabs.btnRefreshc.setEnabled(False)

    def _error(self, mqtt, msg=""):
        self._tabs.btnRefreshc.setEnabled(True)
        Log.progress(msg)


class dsConfigView(QObject):
    def __init__(self, tabs, tLayer, feature):
        super(dsConfigView, self).__init__()
        self._tabs = tabs
        self.pTable = None
        self._topicManager = tLayer.topicManager()
        self._deviceMap = None

        try:
            self._deviceMap = self._topicManager.getDeviceMap(str(feature['topic']))
            _dType = self._topicManager.getDeviceType(self._deviceMap)
            self.pTable = ParameterTable(self._deviceMap, _dType, tabs.tblParams, Constants.Update)
            self._tabs.btnApply.clicked.connect(self._apply)
        except Exception as e:
            Log.debug("Error loading Configuration tab " + str(e))

    def _apply(self):
        if self._topicManager.isDemo():
            Log.progress("Demo mode - no changes can be applied")
            return
        params = self.pTable.params()
        self._deviceMap.set('params', params)
        self._topicManager.setDeviceMap(self._deviceMap)


    def show(self):
        pass

    def update(self, data):
        pass


    def _refresh(self):
        pass

    def _error(self, mqtt, msg=""):
        Log.progress(msg)


class tlDsFeatureDialog(tlFeatureDialog):
    """
    Implementation of tlFeatureDialog.

    """

    @staticmethod
    def _createTab(Tabs, widget):
        idx = Tabs.indexOf(widget)
        return Tabs.widget(idx), Tabs.tabText(idx), idx

    def __init__(self, dialog, tLayer, feature):
        dsTabs = dsDataTab()
        widgets = []
        Tabs = dsTabs.Tabs

        widgets.append(tlDsFeatureDialog._createTab(Tabs, dsTabs.dataTab))
        widgets.append(tlDsFeatureDialog._createTab(Tabs, dsTabs.chartTab))
        widgets.append(tlDsFeatureDialog._createTab(Tabs, dsTabs.configTab))

        super(tlDsFeatureDialog, self).__init__(dialog, tLayer, feature, widgets)
        self._dataTab = dsDataLoggerView(dsTabs, tLayer, feature)
        self._dataTab.show()
        self._chartTab = dsChartView(dsTabs, tLayer, feature)
        self._chartTab.show()
        self._configTab = dsConfigView(dsTabs, tLayer, feature)
        self._configTab.show()

        topic = self._find(QComboBox, 'topic')
        if topic:
            topic.setEnabled(False)
        

    