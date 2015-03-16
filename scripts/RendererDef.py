import arcpy
import json

graduatedColorsDef = {
        "type": "classBreaksDef",
        "classificationField": "DIST_MILES",
        "classificationMethod": "esriClassifyNaturalBreaks",
        "breakCount": 5,
        "colorRamp":
            {
            "type": "algorithmic",
            "fromColor": [255,255,229,255],
            "toColor": [102,37,6,255],
            "algorithm": "esriHSVAlgorithm"
            }
    }

# add with keyword baseSymbol
baseSymbol = {
            "Polyline" : {
                "type": "esriSLS",
                "style": "esriSLSSolid",
                "color": [105,0,140,255],
                "width": 3
                },

            "Point" : {
                "type": "esriSMS",
                "style": "esriSMSCircle",
                "color": [204,0,0,0],
                "size": 8,
                "angle": 0,
                "xoffset": 0,
                "yoffset": 0,
                "outline":
                    {
                    "color": [204,0,0,0],
                    "width": 0
                    }
                },
            "Polygon" :
                {
                "type": "esriSMS",
                "style": "esriSMSSquare",
                "color": [204,0,0,0],
                "size": 8,
                "angle": 0,
                "xoffset": 0,
                "yoffset": 0,
                "outline":
                    {
                    "color": [0,0,0,0],
                    "width": 1
                    }
                }
    }

def getDrawingInfo(descLayer, classificationField):
    '''gives drawingInfo value based on a rendererdef.
    descLayer is the describe object of the layer'''

    rendererDef = graduatedColorsDef
    rendererDef["classificationField"] = classificationField
    rendererDef["baseSymbol"] = baseSymbol[descLayer.shapeType]
    symbLayer = "SymbologyLayer"
    arcpy.MakeFeatureLayer_management(descLayer.catalogPath, symbLayer)
    lyr = arcpy.mapping.Layer(symbLayer)
    lyr._arc_object.setsymbology(rendererDef)
    return json.loads(lyr._arc_object.getsymbology())





