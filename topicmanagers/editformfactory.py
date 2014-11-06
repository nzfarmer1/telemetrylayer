from PyQt4.QtCore import *
from PyQt4.QtGui import *

from TelemetryLayer.lib.tllogging import tlLogging as Log

import traceback,sys

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
    """
    boot loader for the tlFeatureDialog object
    maps layer to tLayer via layer manager
    layer's topic manager available via tLayer
    """
    
    try:
#        layer.startEditing() # Doesn't work
        tLayer = this.layerManager.getTLayer(layer.id())
        myDialogHandler = tLayer.topicManager().featureDialog(dialog,tLayer,feature)
        myDialogHandler.show()
    except Exception as e:
      Log.debug("Problem loading custom feature dialog for " + layer.name())
      exc_type, exc_value, exc_traceback = sys.exc_info()
      Log.debug(repr(traceback.format_exception(exc_type, exc_value,
                      exc_traceback)))

