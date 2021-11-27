#!/usr/bin/env python
# coding: utf8

def readJson(jsonFile):
    import os
    import json
    try:
        if os.path.isfile(jsonFile):
            with open(jsonFile, 'r') as openfile:
                jsonDict = json.load(openfile)
            openfile.close
        else:
            # create Json construct
            jsonDict = {
                "mqtt": {
                    "server": {
                        "_comment": "Remote MQTT-Server, for display and remote control",
                        "address": "replace with ip address",
                        "port": "replace with mqtt port"
                    }
                },
                "modules": {
                    "w1thermsensor": {
                        "imports": [],
                        "functions": {
                            "get-value": "GetValue_W1ThermSensor"
                        }
                    }
                },
                "sensors": {
                    "1-wire": {
                        "_comment" : "new sensors are entered independently by the script",
                        "sensor id": {
                            "type": "type of sensor",
                            "module": "name of module to import",
                            "description": "sensor description"
                        }
                    }
                },
                "actuators": {

                }
            }
    except:
        jsonDict = False

    return(jsonDict)


def writeJson(jsonFile, jsonDict):
    def safe_open_w(path):
        #https://stackoverflow.com/questions/23793987/write-file-to-a-directory-that-doesnt-exist
        #Open "path" for writing, creating any parent directories as needed.
        import os, os.path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return open(path, 'w')

    import json
    # Serializing json
    try:
        jsonObject = json.dumps(jsonDict, indent=100)
        with safe_open_w(jsonFile) as outfile:
            outfile.write(jsonObject)
        outfile.close
        result = True
    except:
        result = False

    return result

def updateJson1Wire(jsonFile, jsonDict):
    def getOneWireAddresses():
        import os
        oneWireDevices = os.listdir("/sys/bus/w1/devices/")
        result = []
        for device in oneWireDevices:
            if not device[:13] == "w1_bus_master":
                result.append(device)

        return result

    writeJsonBool = False
    oneWireAdresses = getOneWireAddresses()
    oneWire = jsonDict['sensors']['1-wire']
    onewireKeys = list(oneWire.keys())
    for address in oneWireAdresses:
        if not address in onewireKeys:
            jsonDict['sensors']['1-wire'][address] = {
                "type": "",
                "module": "",
                "description": ""
            }
            writeJsonBool = True
    if writeJsonBool:
        writeJson(jsonFile, jsonDict)
    return jsonDict