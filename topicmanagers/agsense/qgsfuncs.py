from qgis.utils import qgsfunction, QgsExpression
import json
from TelemetryLayer.lib.tllogging import tlLogging as Log

@qgsfunction(0, u"Telemetry Layer")
def agsense_format_label(values, feature, parent):
    try:
        if  int(feature.attribute('visible'))  == 0:
            return ""
        else:
            Log.debug(feature.attribute('payload'))
            payload = json.loads(feature.attribute('payload'))
            return str(feature.attribute('name')) + '\n(' + str(payload['raw']) + ')'
    except:
        return str(feature.attribute('name')) + '\n(' + str(feature.attribute('payload')) + ')'
        pass

@qgsfunction(0, u"Telemetry Layer")
def agsense_alert(values, feature, parent):
    """
    Returns true if an alert has been raised. False otherwise.
    """
    try:
        return int(feature['alert']) == 1 or feature['alert'] == 'true' or feature['alert'] == 'True'
    except:
        return False
        pass

