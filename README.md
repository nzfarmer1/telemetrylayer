telemetrylayer
==============

QGIS Plugin to integrate QGIS with MQTT


Target platform QGIS 2.4

Latest changes:

1. Refactored code - seperate topic managers from brokers
2. Examples of V2EditWidgets in topic managers provided
3. Added Dock Views
4. Multiple minor enhancements

Features:

1. Broker manager to manage a list of brokers and connection parameters
2. Topic Managers (extensible) to support different "types" of Topics and Layer Formats
3. Integration with MQTT via Mosquitto/Paho client library
4. Connections and updates within dedicated thread

Usage:
 
1. Enter Settings to start adding your brokers
2. Create a New Telemetry (Point) Layer - selecting the Broker and Topic Type
3. Add Features - enter name, topic
4. Edit features (double click on Broker Group in legend then double click on feature (respects edit layer edit mode)

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

- integrate with QGIS native help with splash screen showing new features
- linux testing of custom feature form (done. needed to replace inbuilt custom feature form)
- document topic manager API
- Add support for 3rd party registration of topic managers
- Address Nathan's code review



If you want to help with any of this, please get in touch!!!

Andrew McClure <andrew@agsense.co.nz>

