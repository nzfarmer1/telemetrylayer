from qgis.utils import qgsfunction, QgsExpression


@qgsfunction(0, u"Telemetry Layer")
def agsense_format_label(values, feature, parent):
    try:
        if  int(feature.attribute('visible'))  == 0:
            return ""
        else:
            return str(feature.attribute('name')) + '\n(' + str(feature.attribute('payload')) + ')'
    except:
        pass

@qgsfunction(0, u"Telemetry Layer")
def agsense_alert(values, feature, parent):
    """
    Returns true if an alert has been raised. False otherwise.
    """
    try:
        return int(feature['alert']) == 1 or feature['alert'] == 'true' or feature['alert'] == 'True'
    except KeyError:
        return False

