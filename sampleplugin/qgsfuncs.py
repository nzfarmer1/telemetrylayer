from qgis.utils import qgsfunction, QgsExpression
from TelemetryLayer.lib.tllogging import tlLogging as Log
import json

@qgsfunction(0, u"Telemetry Layer")
def sample_format_label(values, feature, parent):
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
                return "<b style=font-size:14pt>Sample Topic Manager<br/>" + str(payload['format']) + "</b>"
        except (KeyError,ValueError,TypeError):
            try:
                return "<b style=font-size:14pt>Sample Topic Manager<br/>" + str(feature.attribute('payload')) + "</b>"
            except:
                return "<b style=font-size:14pt>n/a</b>"
            
    # default context (map)

    try:
        if int(feature.attribute('visible'))  == 0:
            return ""
        else:
            payload = json.loads(feature.attribute('payload'))
            return str("Sample Topic Manager\n") + str(feature.attribute('name')) + '\n(' + str(payload['format']) + ')'
    except (KeyError,ValueError,TypeError):
        try:
            return str(feature.attribute('match')) + '\n(' + str(feature.attribute('payload')) + ')'
        except:
            return "n/a"
