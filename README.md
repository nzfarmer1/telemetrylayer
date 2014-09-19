telemetrylayer
==============

QGIS Plugin to integrate QGIS with MQTT


Target platform QGIS 2.4

Features:

1. Broker manager to manage a list of brokers and connection parameters
2. Topic Managers (extensible) to support different "types" of Topics and Layer Formats
3. Integration with MQTT via Mosquitto client library
4. Connections and updates within dedicated thread

Usage:
 
1. Enter Settings to start adding your brokers
2. Select a Generic MQTT broker for a topic manager
3. Create a New Telemetry (Point) Layer - selecting the Broker and Topic Type
4. Add Features based on topics generated via the Topic Manager (i.e. Broker Uptime)

Installation:

To install and run locally, copy recursively into a ~/.qgis2/python/plugins/TelemetryLayer directory then enable the plugin

A public repo will be created soon

Issues:

This is very alpha software and still has many features not implemented.
It is recommended for developers only and must NOT be used on production projects!
We accept no liability

The code has been developed on a Mac using OSX 10.9.4 and although it runs on Windows and Linux, it is not stable.

Am looking for assistance to bring the plugin to an improved state of maturity.

Note: please forgive my coding. This was my first major python development and you will see
the some variance in style as I matured in its use and became more familiar with the QGIS APIs
and python libraries.

Constructive feedback is welcome

TODO:

This is my top list. There's lots more of course!

- setEditForm and setEditFormInit only seem to work on my Mac.  See tlabstracttopicmanager.py
- replace mosquitto client with paho.Client()
- on windows, labels are not shown until layer settings are entered, and clicked Ok
- rules based symbology is required, and needs to be configured programatically with changes
for 'updated','changed' etc. again, see tlabstracttopicmanager.



Andrew McClure <andrew@southweb.co.nz>

