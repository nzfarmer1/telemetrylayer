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
