#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      arok5348
#
# Created:     10/03/2015
# Copyright:   (c) arok5348 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
import json
from RendererDef import getDrawingInfo
from ProcessRestRequest import getResponse
from identity import getIdentity

def main():
    #get Token
    params= {}
    params["f"] = "json"
    params["username"] = username
    params["password"] = password
    params["client"] = "referer"
    params["referer"] = referer
    params["expiration"] = 60
    token, tokenStatus = getToken(params)
    if tokenStatus == "ok":
        params = {"token":token, "f":"json"}
        userInfo = getSelfProperties(params, referer)
        if checkPrivilege(userInfo, "portal:user:createItem"):
            descLyr = arcpy.Describe(featureClass)
            featureColl = createFeatureCollectionJSON(descLyr)
            extent = descLyr.extent
            itemParams = createItemJSON(featureColl, extent)
            #username = userInfo["user"]["username"]
            #add token to itemParams
            itemParams.update(params)
            agolItemInfo = createAGOLFCItem(itemParams, token, referer)
            arcpy.SetParameterAsText(5, agolItemInfo)

    else:
        print tokenStatus




def getToken(queryParams):

    try:
        token_url ="{}/generateToken".format(portalUrl)
        tokenStatus = ""
        resp = getResponse(token_url, queryParams)
        response = json.loads(resp)
        if "token" in response:
            token = response["token"]
            tokenStatus += "ok"
        elif "error" in response:
            token = ""
            msgs = response['error']
            tokenStatus += msgs['message']
            details = msgs['details']
            if isinstance(details, list):
                tokenStatus += "\n".join(details)
            else:
                tokenStatus += details
        elif response.get("status") == "error":
            token = ""
            details = response.get('messages')
            if isinstance(details, list):
                tokenStatus += "\n".join(details)
            else:
                tokenStatus += details
        return token, tokenStatus

    except Exception as ex:
        print "unable to retrieve token"
        tokenStatus = False
        print str(ex)
        return None, False


def createAGOLFCItem(itemJSON, token, referer):
    '''creates specified FC item in given portal_url
   '''
    try:
        addItemUrl = "{}/content/users/{}/addItem".format(portalUrl, username)
        resp = getResponse(addItemUrl, itemJSON, referer)
        resultJSON = json.loads(resp)
        if "success" in resultJSON and resultJSON["success"]:
            itemID = resultJSON["id"]
            #arcpy.AddMessage("added item successfully: {}".format(itemID))
            itemUrl = "{}/content/items/{}".format(portalUrl,itemID)
            arcpy.AddMessage(itemUrl)
            return json.dumps({"url":itemUrl, "itemId":itemID})
        else:
            raise Exception(resultJSON)
    except Exception as e:
        arcpy.AddMessage(str(e))
        arcpy.AddMessage("itemCreation failed")
        return None

def createFeatureCollectionJSON(descLayer):
    '''create featurecollection json'''

    layerJSON = {"layerDefinition":{},
                 "featureSet":{},
                 }

    fsJSON = json.loads(arcpy.FeatureSet(descLayer.catalogPath).JSON)
    fields = fsJSON.pop("fields")
    spRef = fsJSON.pop("spatialReference")
    fsJSON.pop("displayFieldName")
    layerJSON["featureSet"] = fsJSON
    layerJSON["layerDefinition"] = {
             "geometryType":fsJSON["geometryType"],
              "objectIdField":descLayer.OIDFieldName,
              #"type":"Feature Layer",
              "drawingInfo":getDrawingInfo(descLayer, symbologyField),
              "fields":fields,
              "types":[],
              "capabilities": "Query",
              "name":itemProperties["title"],
              "extent":json.loads(descLayer.extent.JSON)
              }
##    if popupInfo:
##        layerJSON["popupInfo"] = popupInfo
    fcJSON = {"layers":[layerJSON],"showLegend":True}
    return fcJSON

def createItemJSON(fcJSON, extent):
        '''creates item JSON'''

        itemJSON = {}
        itemJSON.update(itemProperties)
        itemJSON.update({
                  "type":"Feature Collection",
                  "typeKeywords":"Data, Feature Collection, Singlelayer",
                  "text": json.dumps(fcJSON),
                  "extent":"{},{},{},{}".format(extent.XMin, extent.YMin, extent.XMax, extent.YMax),
                  })
        return itemJSON


def getSelfProperties(params, referer):
    '''gets the token, referer, portal_url, username from hostedgp'''
    try:
       selfUrl = "{}/portals/self".format(portalUrl)
       resp = getResponse(selfUrl, params, referer)
       selfResp = json.loads(resp)
       return selfResp
    except Exception as e:
        arcpy.AddMessage(str(e))
        return None

def checkPrivilege(selfJSON, privilege):
    '''checks given privilege'''
    try:
        return privilege in selfJSON["user"]["privileges"]
    except Exception as e:
        arcpy.AddMessage(str(e))
        arcpy.AddError("Unable to verify user privilege")


if __name__ == '__main__':

    portalUrl = "https://www.arcgis.com/sharing/rest"
    referer = "https://www.arcgis.com"
    username, password = getIdentity()
    itemProperties = {  "title":arcpy.GetParameterAsText(2),
                        "snippet":arcpy.GetParameterAsText(4),
                        "tags":arcpy.GetParameterAsText(3).replace(";", ",")
                     }

    symbologyField = arcpy.GetParameterAsText(1)
    featureClass = arcpy.GetParameterAsText(0)
    main()
