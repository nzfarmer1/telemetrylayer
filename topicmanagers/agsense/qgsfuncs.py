from qgis.utils import qgsfunction, QgsExpression
from TelemetryLayer.lib.tllogging import tlLogging as Log
import json

@qgsfunction(0, u"Telemetry Layer")
def agsense_format_label(values, feature, parent):
    try:
        context = feature['context']
    except:
        context  = 'map'

    if context == 'dock-title' or context == 'feature-list':
        try:
            payload = json.loads(feature.attribute('payload'))
            return str(payload['format'])
        except (KeyError,ValueError,TypeError):
            try:
                return str(feature.attribute('payload'))
            except:
                return "n/a"

    if context == 'dock-content':
        try:
            if int(feature.attribute('visible'))  == 0:
                return ""
            else:
                payload = json.loads(feature.attribute('payload'))
                return "<b style=font-size:72pt>" + str(payload['format']) + "</b>"
        except (KeyError,ValueError,TypeError):
            try:
                return "<b style=font-size:72pt>" + str(feature.attribute('payload')) + "</b>"
            except:
                return "<b style=font-size:72pt>n/a</b>"
            
    # default context (map)

    try:
        if int(feature.attribute('visible'))  == 0:
            return ""
        else:
            payload = json.loads(feature.attribute('payload'))
            return str(feature.attribute('name')) + '\n(' + str(payload['format']) + ')'
    except (KeyError,ValueError,TypeError):
        try:
            return str(feature.attribute('match')) + '\n(' + str(feature.attribute('payload')) + ')'
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

