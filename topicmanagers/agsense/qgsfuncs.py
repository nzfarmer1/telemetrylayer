from qgis.utils import qgsfunction, QgsExpression
from TelemetryLayer.lib.tllogging import tlLogging as Log
import json

@qgsfunction(0, u"Telemetry Layer")
def agsense_format_label(values, feature, parent):
    try:
        if  int(feature.attribute('visible'))  == 0:
            return ""
        else:
            payload = json.loads(feature.attribute('payload'))
            return str(feature.attribute('name')) + '\n(' + str(payload['format']) + ')'
    except (KeyError,ValueError):
        try:
            return str(feature.attribute('name')) + '\n(' + str(feature.attribute('payload')) + ')'
        except:
            return "n/a"

@qgsfunction(0, u"Telemetry Layer")
def agsense_alert(values, feature, parent):
    """
    Returns true if an alert has been raised. False otherwise.
    """
    try:
            payload = json.loads(feature.attribute('payload'))
            return payload['alert'] == 'AlertOn' # change constant as required
    except:
        return False
        pass

