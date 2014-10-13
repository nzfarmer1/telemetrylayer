# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DigiSenseDeviceMappingDialog
 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from TelemetryLayer.lib.tlsettings import tlSettings as Settings, tlConstants
from TelemetryLayer.lib.tllogging import tlLogging as Log
from TelemetryLayer.tlmqttclient import *

from ui_dsdevicemapdialog import Ui_dsDeviceMapDialog
from dsdevicemaps import   dsDeviceMap as DeviceMap, dsDeviceMaps as DeviceMaps

import traceback, sys


class tlTableParam(QObject):

    LABEL = 0
    CONTROL = 1

    def __init__(self,tbl,row,param,default = None):
        super(tlTableParam,self).__init__()
        tbl.insertRow(row)

        self.row = row
        self.tbl = tbl
        self.value = default
        self.control = QWidget()
 
        try:
            self.name = param.get('name')
            self.title = param.get('title')
            self.tooltip = param.get('description')
            self.type = param.find('Type').text
            if default == None:
                try:
                    self.default = param.find('Default').text
                except:
                    self.default = 1
            else:
                self.default = default
        
        except TypeError as e:
            Log.warn('Type error creating paramater widget ' + str(e))
            
        item = QtGui.QLabel(self.title,self.tbl)
        item.setStyleSheet("padding: 4px")
        item.setWordWrap(True)
        item.setToolTip(self.tooltip)

        self.tbl.setCellWidget(row,self.LABEL, item)
        
        item = QtGui.QTableWidgetItem(0)
        item.setFlags(QtCore.Qt.NoItemFlags)
        tbl.setItem(row,self.LABEL,item)
        
        pass

    def _setControl(self,height = None):
        self.tbl.setCellWidget(self.row,self.CONTROL,self.control)
        item = QtGui.QTableWidgetItem(0)
        item.setFlags(QtCore.Qt.NoItemFlags)
        self.tbl.setItem(self.row,self.LABEL,item)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        if height !=None:
            self.tbl.setRowHeight(self.row,height)

    
    def getName(self):
        try:
            return self.name
        except:
            return None

    
    def getTitle(self):
            return self.title
    
    def getValue(self):
       return self.value

    def getType(self):
       return self.type

# Create a spin box

class tlTableParamSpinBox(tlTableParam):
    def __init__(self,tbl,row,param,default = None):
        super(tlTableParamSpinBox,self).__init__(tbl,row,param,default)

        try:    
            self.min = param.find('Min').text
            self.max = param.find('Max').text
            self.int = param.find('Interval').text
            self.units = param.find('Units').text
            try:
                self.step = param.find('Step').text
            except:
                self.step = "1"

            self.control = QtGui.QSpinBox(self.tbl)
            self.control.setMinimum(int(self.min)-1) # Qt Bug Min is actual > not >=
            self.control.setMaximum(int(self.max))
            self.control.setSingleStep(int(self.step)) #???
            self.control.setToolTip(self.tooltip)
            self.control.setSuffix('\x0A' + self.units)
            self.control.setStyleSheet("padding: 4px")
            self.control.valueChanged.connect(self.setValue)
            self._setControl(40)
            self.control.setValue(int(self.default))
         

        except Exception as e:
            Log.debug('Error loading parameter widget ' + str(e))
            return

        pass
    
    def setValue(self,value):
        self.value = value

        
# Create a Slider

class tlTableParamSlider(tlTableParam):
    def __init__(self,tbl,row,param,default = None):

        super(tlTableParamSlider,self).__init__(tbl,row,param,default)
        try:    
            self.min = param.find('Min').text
            self.max = param.find('Max').text
            self.int = param.find('Interval').text
            self.units = param.find('Units').text
            try:
                self.step = param.find('Step').text
            except:
                self.step = "1"

            # Only handles Integers currently!
    
            self.control = QtGui.QSlider(QtCore.Qt.Horizontal,self.tbl)
            self.control.setFocusPolicy(QtCore.Qt.ClickFocus)
            #self.control.setTickPosition(QtGui.QSlider.TicksBelow)
            #self.control.setTickInterval(int(float(self.max)/50))
            self.control.setSingleStep(int(self.step))
            self.control.setMinimum(int(self.min))
            self.control.setMaximum(int(self.max))
            self.control.setToolTip(self.tooltip)
            self.control.setStyleSheet("padding: 4px")
            self.control.valueChanged.connect(self.setValue)
    
            self._setControl(50)
          
            self.control.setValue(int(self.default))

        except Exception as e:
            Log.warn('Error creating widget parameter ' + str(e))
            return

    def setValue(self,value):
        self.value = value
        item = self.tbl.cellWidget(self.row,self.LABEL)
        item.setText(self.title + ' ' + str(value) +  ' ' + self.units)
        pass


# Create a Dropdown

class tlTableParamCombo(tlTableParam):
    def __init__(self,tbl,row,param,default=None):

        super(tlTableParamCombo,self).__init__(tbl,row,param,default)
    
        # Only handles Integers currently!
        
        self.control = QtGui.QComboBox(tbl)
        self.control.setToolTip(self.tooltip)
        idx = 0
        defidx = 0
        for option in param.find('Options'):
            self.control.insertItem(idx,option.text,option)
            if option.get('value') == self.default:
                defidx = idx
            idx = idx+1
            
        self.control.currentIndexChanged.connect(self.setValue)
        self.control.setToolTip(self.tooltip)
        self._setControl()
        #self.tbl.setRowHeight(row,100)
        self.control.setCurrentIndex(defidx)

    def setValue(self,idx):
        self.value = self.control.itemData(idx).get('value')
        pass



# Class to handle mapping of physical with a logical device
# Mappings are currently 1<=>1

class dsDeviceMapDialog(QtGui.QDialog, Ui_dsDeviceMapDialog):

    def __init__(self,creator,devicemap = None):
        super(dsDeviceMapDialog, self).__init__()
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        
        self._creator = creator
        self._broker = creator._broker
        self._deviceMap = devicemap
        self._deviceTypes = None
        self._deviceMaps = None
        self._curDeviceIdx = None
        self.params =[]
        self.mode = tlConstants.Create # By default we are in create mode
        self.dirty = False

        self.setupUi()
        pass

    def setupUi(self):
        super(dsDeviceMapDialog,self).setupUi(self)
        try:
            self._deviceTypes = self._creator.getDeviceTypes()
            self.devicesMaps = self._creator.getDeviceMaps()
            self.deviceKeyLabel.setText(self._deviceMap.getDeviceKey())
            
            if self._deviceMap.getDeviceTypeId() != None and self._deviceMap.getTopic() != None:
                self.mode = tlConstants.Update
            
            self.createTypesCombo(self._deviceMap.getDeviceTypeId())
            self.applyButton.clicked.connect(self.validateApply)

            noSpaceValidator= QRegExpValidator(QRegExp("^[\$A-Za-z0-9\/]+"),self);
            self.topic.setValidator(noSpaceValidator)
            self.topic.setReadOnly(True)
            if self._deviceMap.getTopic() != None:
               self.topic.setText(self._deviceMap.getTopic())

            spaceValidator= QRegExpValidator(QRegExp("^[a-zA-Z0-9 ]+"),self);
            self.name.setValidator(spaceValidator)
            if self._deviceMap.getName() !=None:
               self.name.setText(self._deviceMap.getName())

            if self.mode == tlConstants.Create:
                self.name.textEdited.connect(self.nameChanged)
                self.deleteButton.hide()
            elif self.mode == tlConstants.Update:
                self.topic.setDisabled(True)
                self.deviceType.setDisabled(True)
                self.deleteButton.clicked.connect(self.validateDelete)
            
#            QObject.connect(self._creator, QtCore.SIGNAL("deviceMapsLoaded"), self.mapsReloaded)

        except Exception as e:
            Log.warn("Error loading catalog of Device Types " + str(e))

    # Create Dropdown of the Device Type Catalog

    def createTypesCombo(self,deviceTypeId =None):
        self.deviceType.addItem('Unspecified',None)
        
        idx = 1 # After adding empty index
        for dtype in self._deviceTypes.values():
            try:
                if dtype.type() != self._deviceMap.getType():
                    continue
                # Add type to drop down
                self.deviceType.addItem(dtype.op() + ' (' + dtype.find('Manufacturer') + ' ' + dtype.find('Model') + ')',dtype)
                
                if deviceTypeId != None and dtype.id() == deviceTypeId:
                    self.deviceType.setCurrentIndex(idx)

                idx = idx + 1
            except Exception as e:
                Log.warn(dtype.id() + " " + str(e))
            
            self.deviceType.currentIndexChanged.connect(self.deviceTypeIndexChanged)
            self.deviceTypeIndexChanged( self.deviceType.currentIndex())

    def nameChanged(self,_str):
        replacement = '/digisense/maps/' + _str.lower().replace(' ','/')
        self.topic.setText(replacement)

    def getDeviceMaps(self):
        return self._deviceMaps
    
    def setDeviceMaps(self,deviceMaps):
        self._deviceMaps = deviceMaps

    def deviceTypeIndexChanged(self,i):
        self.applyButton.setDisabled(i == 0)
        if (i == 0):
            return
        if self._curDeviceIdx != self.deviceType.itemData(i):
            self._curDeviceIdx = self.deviceType.itemData(i)
            self.createParameterTable(self._curDeviceIdx)

    def _deleteMapCallback(self,client,status,response):
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor));
        self.applyButton.setDisabled(False)
        if status == True:
            self.setDeviceMaps(DeviceMaps.decode(response))
            self.dirty = True
            #self._creator._buildDevicesTables() # Replace with SIGNAL?
            #QObject.emit(self._creator,QtCore.SIGNAL("deviceMapsRefreshed"))
            Log.progress("Device map deleted")
            self.accept()
        else:
            Log.progress("Unable to update map: " + response)

# Validate deletion of a Device Map

    def validateDelete(self,status):
        msg = "Are you sure you want to delete this mapping?  Please note you will need to edit/delete any features that use this Topic"
        if not Log.confirm(msg):
            return
        self._deviceMap.unset('name')
        self._deviceMap.unset('topic')
        self._deviceMap.unset('params')
        self._deviceMap.unsetDeviceTypeId()
        try:
            # Implement this!!!
            self.deleteButton.setDisabled(True)
            self.applyButton.setDisabled(True)
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
            aClient = tlMqttSingleShot(self,
                                      self._broker.host(),
                                      self._broker.port(),
                                      "/digisense/request/update/map",
                                      "/digisense/response/device/maps",
                                      self._deviceMap.dumps())
            QObject.connect(aClient, QtCore.SIGNAL("mqttOnCompletion"), self._deleteMapCallback)
            aClient.run()
            self.mode = tlConstants.Deleted
        except:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
            Log.debug("Error deleting map: " + str(e))

    def _updateMapCallback(self,client,status,response):
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor));
        self.applyButton.setDisabled(False)
        if status == True:
            self.setDeviceMaps(DeviceMaps.decode(response))
            self.dirty = True
            
            Log.progress("Device map updated")
            
            self.accept()
        else:
            Log.progress("Unable to update map: " + response)
            
            
    # Apply changes to individual map            
    
    def validateApply(self,status):
        Log.debug("Apply")   
        
        if len(self.name.text()) < 8:
            Log.alert("Please ensure the name is at least 8 characters long")
            return
        
        try:
            dtype =   self.deviceType.itemData(self.deviceType.currentIndex())
            params = {}
            for param in self.params:   
                params[param.getName()] = param.getValue()
                Log.debug("Setting " + param.getName() + " to " + str(param.getValue()))
            self._deviceMap.setDeviceTypeId(dtype.id()) 
            self._deviceMap.set('name',self.name.text()) 
            self._deviceMap.set('topic',self.topic.text()) 
            self._deviceMap.set('manufacturer',dtype.manufacturer()) 
            self._deviceMap.set('model',dtype.model()) 
            self._deviceMap.set('units',dtype.units()) 
            self._deviceMap.set('params',params) 
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
            self.applyButton.setDisabled(True)
            
            aClient = tlMqttSingleShot(self,
                                      self._broker.host(),
                                      self._broker.port(),
                                      "/digisense/request/update/map",
                                      "/digisense/response/device/maps",
                                      self._deviceMap.dumps())
            QObject.connect(aClient, QtCore.SIGNAL("mqttOnCompletion"), self._updateMapCallback)
            aClient.run()
        except Exception as e:
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor));
            Log.debug("Error saving map " + str(e))

        
    def mapsReloaded(self):
            Log.alert("Device information updated.")
            if self.mode == tlConstants.Deleted:
                self.accept()
                return
            self.applyButton.setDisabled(False)

  
    def createParameterTable(self,dtype):

        tblParam = self.parameterTable
        tblParam.horizontalHeader().setVisible(False)
        tblParam.verticalHeader().setVisible(False)

        del self.params[:]
        
        tblParam.clearContents()
        tblParam.setRowCount(0)
        tblParam.setShowGrid(True)
        tblParam.setColumnCount(2);
       
        if dtype == None:
            return
        
        params = dtype.params()
        if (params == None or len(params) == 0):
            return
        
        # Create a table of controls preset with existing values if required
        # Parameters are defined in the device maps XML
        
        for param in params:
            default = None
            if self.mode == tlConstants.Update:
                default = self._deviceMap.getParam(param.get('name'))
            
            if param.get('widget') == 'slider':
                self.params.append(tlTableParamSlider(tblParam,tblParam.rowCount(),param,default))
            if param.get('widget') == 'select':
               self.params.append(tlTableParamCombo(tblParam,tblParam.rowCount(),param,default))
            if param.get('widget') == 'spinbox':
               self.params.append(tlTableParamSpinBox(tblParam,tblParam.rowCount(),param,default))
         

#    def accept(self):
#        Log.debug("accept")
#        super(dsDeviceMapDialog,self).accept()
        

    def __del__(self):
        del self.params[:]
        pass

