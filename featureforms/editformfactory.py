from PyQt4.QtCore import *
from PyQt4.QtGui import *

"""
/***************************************************************************
 loadfeatureform
                                 A QGIS plugin
                             -------------------
        begin                : 2014-05-30
        copyright            : (C) 2014 by Andrew McClure
        email                : andrew@southweb.co.nz
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 
 This package has a single method - featureDialog - which is used to provide
 an instance
 
 
"""


this = None



def featureDialog(dialog,layer,feature):
	try:
		tLayer = this.layerManager.getTLayer(layer.id())
		myDialogHandler = tLayer.topicManager().featureDialog(dialog,tLayer,feature)
		myDialogHandler.show()
		
	except Exception as e:
		print "Problem loading custom feature dialog for " + layer.name()
		print str(e)
		




def _featureDialog(dialog,layer,feature):
    global myDialog
    myDialog = dialog
    global nameField
    nameField = dialog.findChild(QLineEdit,"name")
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")

    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.rejected.connect(validate)
    #buttonBox.rejected.connect(myDialog.reject)

def validate():
	 msgBox = QMessageBox()
	 msgBox.setText("Validating.")
	 msgBox.exec_()
	 myDialog.accept()
