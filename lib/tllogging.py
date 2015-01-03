# -*- coding: utf-8 -*-
from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import QObject,  SIGNAL
from PyQt4.QtGui import QDockWidget
from qgis.core import QgsMessageLog
from PyQt4.QtGui import QProgressBar
from qgis.gui import QgsMessageBar
from tlsettings import tlSettings as Settings
import os, urllib, webbrowser

"""
 tlLogging
 
 Wrapper for Logging related functions
"""

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class tlLogging(QObject):

    HEADER   = ''
    CRITICAL = 1
    INFO     = 2
    WARN     = 4
    DEBUG    = 8
    STATUS   = 16

    _iface  = None
    _pstack = {}
    _logDock = None
    _logStates = CRITICAL | DEBUG

    def __init__(self,creator):
        super(tlLogging,self).__init__()
        tlLogging._iface = creator.iface
        tlLogging._logDock = tlLogging._iface.mainWindow().findChild(QDockWidget, 'MessageLog')
        tlLogging.HEADER = Settings.getMeta('name','general')
        tlLogging._logStates = int(Settings.get("logStates",tlLogging._logStates))

    @staticmethod
    def logDockVisible():
        return tlLogging._logDock.isVisible()

    @staticmethod
    def setLogStates(logStates):
        Settings.set("logStates",logStates)
        tlLogging._logStates = logStates
        tlLogging.status("",True)

    @staticmethod
    def path2url(path):
        """Return file:// URL from a filename."""
        path = os.path.abspath(path)
        if isinstance(path, unicode):
            path = path.encode('utf8')
        return 'file:' + urllib.pathname2url(path)

    @staticmethod
    def openFileInBrowser(file_name):
        if os.path.basename(file_name) == file_name:
            file_name = os.path.join(Settings.get("plugin_dir"),file_name)
        if os.path.exists(file_name):
            webbrowser.open(tlLogging.path2url(file_name))


    @staticmethod
    def alert(msg):
        msgBox = QtGui.QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()
        return

    @staticmethod
    def confirm(msg):
        msgBox = QtGui.QMessageBox()
        msgBox.setText(msg)
        msgBox.addButton(QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(msgBox.addButton(QtGui.QMessageBox.Ok))
        result = msgBox.exec_()
        return result == QtGui.QMessageBox.Ok


    @staticmethod
    def status(msg,force = False):
        if tlLogging._iface != None and (tlLogging._logStates & tlLogging.STATUS) or force:
            tlLogging._iface.mainWindow().statusBar().showMessage(str(msg))

    @staticmethod
    def progressPush(msg):
        tlLogging._pstack[msg] = tlLogging.progress(msg,0)

    @staticmethod
    def progressPop(msg):
        if msg in tlLogging._pstack:
            tlLogging._iface.messageBar().popWidget(tlLogging._pstack[msg])
            del tlLogging._pstack[msg] 

    @staticmethod
    def progress(msg,duration = 3,level = QgsMessageBar.INFO):
        if tlLogging._iface != None:
                widget  = QtGui.QLabel(str(msg))
                widget.setStyleSheet("QLabel {padding-left:40px;padding-top:50px;padding-bottom:50px;background-image:url(':/plugins/telemetrylayer/icons/southweb.png');background-repeat:no-repeat; background-origin:left}")         
                return tlLogging._iface.messageBar().pushWidget(widget,QgsMessageBar.INFO,duration)


    @staticmethod
    def progressX(msg,duration = 0):
        if tlLogging._iface != None:
                tlLogging._iface.messageBar().pushMessage(tlLogging.HEADER,msg, QgsMessageBar.WARNING,duration)

    @staticmethod
    def info(msg,level = QgsMessageLog.INFO):
        if tlLogging._logStates & tlLogging.INFO:
            QgsMessageLog.logMessage(str(msg),tlLogging.HEADER,level)


    @staticmethod
    def warn(msg,level = QgsMessageLog.WARNING):
        if tlLogging._logStates & tlLogging.WARN:
           QgsMessageLog.logMessage(str(msg),tlLogging.HEADER,level)

    @staticmethod
    def debug(msg,level = QgsMessageLog.INFO):
        if tlLogging._logStates & tlLogging.DEBUG:
            QgsMessageLog.logMessage(str(msg),tlLogging.HEADER,level)

    @staticmethod
    def critical(msg,duration = 00):
        if not tlLogging._logStates & tlLogging.CRITICAL:
            return
        QgsMessageLog.logMessage(str(msg),tlLogging.HEADER,QgsMessageLog.CRITICAL)
        if tlLogging._iface != None:
                widget  = QtGui.QLabel(str(msg))
                widget.setStyleSheet("QLabel {padding-left:40px;background-image:url(':/plugins/telemetrylayer/icons/icon.png');background-repeat:no-repeat; background-origin:left}")         
                return tlLogging._iface.messageBar().pushWidget(widget,QgsMessageBar.CRITICAL,duration)
