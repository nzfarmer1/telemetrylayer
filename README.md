telemetrylayer
==============

QGIS Plugin to integrate QGIS with MQTT


Target platform QGIS 2.8

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

To install and use the Sample Plugin:
1. Clone the git
2. Copy the sampleplugin folder to your QGIS plugins folder (i.e. ~/.qgis2/python/plugins)
3. Enable it via the Plugins menu

Note:

Right now I have only 3 types of topic manager/widget interfaces.  And the logic for controlling the SVG gauge is not written.

However, as this release represents a major refactor with many fixes - and flags the shape of things to come - I release it now so that the Plugin can be reviewed and those interested to assist can come on board.

The architecture now is quite solid with much flexibility in determining the representation of a widget

Some architectural insights below:

- Topic managers are singleton stateless sub classes from the main tlTopicManager class 
- They allow fine grained configuration of the layer's rules, symbols, addtional feature fields, widgets and formatters
- qgsfunctions are used extensively - feature['context'] field is used so that the formatting of the payload can be context sensitive. Custom qgsfunctions can also be used to flag an alert state.
- to view data within the dock view (see Feature List then double click a feature) FeatureDock is sub classed.  Instead of subclassing the base class you can subclass the Text, Form, or SVG FeatureDocks.  See examples under topicmanager folder.

Notes on version numbers:  these have been handled badly. The code < 1 but we were forced to use 1 when moving to a.b.c version format.  Please consider 1.x.x to be alpha.  2.x.x beta. And 3.x.x production when we get there.



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
- document topic manager API
- Add support for 3rd party registration of topic managers
- Add additional FeatureDock/TopicManager types. Get SVG graphics for instruments working
- Change reading .qml files to python code when formatting a layer's Rulei based renderer
- Create / extend SVG Feature Dock functionality
- Improve memory usage and Add plugin reloader support for dynamicly created topicmanagers


If you want to help with any of this, please get in touch

Andrew McClure <andrew@agsense.co.nz>

