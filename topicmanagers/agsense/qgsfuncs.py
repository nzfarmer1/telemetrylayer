from qgis.utils import qgsfunction, QgsExpression


@qgsfunction(0, u"Telemetry Layer")
def agsense_format_label(values, feature, parent):
    result = "No data"
    try:
        visible = int(feature.attribute('visible'))
        if visible == 0:
            result = ""
        else:
            result = str(feature.attribute('name')) + '\n(' + str(feature.attribute('payload')) + ')'
    except:
        pass
    finally:
        return result
