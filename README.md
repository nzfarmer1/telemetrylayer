telemetrylayer
==============

QGIS Plugin to integrate QGIS with MQTT


Target platform QGIS 2.4

Latest changes:

1. Added support for V2 style attribute widgets
2. Added support for visible/invisible features (partial)
3. Added support to change  Granted QoS value (not supported by Mosquitto)
4. Removed Broker ID and Type from layer attributes and hid remaining attributes

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

The code has been developed on a Mac using OSX 10.9.4.

Am looking for assistance to bring the plugin to an improved state of maturity.

The latest release fixes a lot of issues. See the commit change log in GIT

Constructive feedback is welcome

TODO:


This is my top list. There's lots more of course!

- add support for roll back/undo when adding/deleting/updating features (Deleting done)
- extend rules based renderer for layers with better examples
- icons for symbols and application - including sensor state symbology
- support to add / edit parameters as additional feature attributes (Done via Feature tab - server side changes only)
- integrate with QGIS native help with splash screen showing new features
- replace mosquitto client with paho.Client

- set default broker config tab to be list of brokers
- add details of broker port/host etc when creating new layer
- ensure topics can only be added as a feature once?
- linux testing of custom feature form


    
        

If you want to help with any of this, please get in touch!!!

Andrew McClure <andrew@southweb.co.nz>

