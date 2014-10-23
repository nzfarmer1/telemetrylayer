# -*- coding: utf-8 -*-

import os
"""
/***************************************************************************
 Telemetry Layer
                                 A QGIS plugin
 Interface to Telemetry Layer sensor network
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
 This script initializes the plugin, making it known to QGIS.
"""

def path():
    return os.path.dirname(__file__)

def classFactory(iface):
    # load FarmSense class from file FarmSense
    from telemetrylayerplugin import TelemetryLayerPlugin
    return TelemetryLayerPlugin(iface)
