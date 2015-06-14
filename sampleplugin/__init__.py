# -*- coding: utf-8 -*-

import os

"""
/***************************************************************************
Sample Plugin TopicManager for Telemetry Layer
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
    from sampleplugin import TelemetryLayerSampleTopicManager

    return TelemetryLayerSampleTopicManager(iface)
