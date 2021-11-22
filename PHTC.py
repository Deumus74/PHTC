#!/usr/bin/env python
#coding: utf8

# Plants Hibernation Tent Control

# region imports
from types import GetSetDescriptorType
from pymodules import PHTCstandard
from pymodules import PHTCjson
import importlib
import os
import sys
import time
import RPi.GPIO as GPIO

# endregion

# region functions


def Round(x, n): return eval('"%.' + str(int(n)) + 'f" % ' + repr(x))


def dynamic_import(module):
    # thanks to https://www.blog.pythonlibrary.org/2016/05/27/python-201-an-intro-to-importlib/
    return importlib.import_module(module)

def getSensorValues(sensorType, id ):
    global json
    global module
    if not id == "_comment":
        tempModule = module[json['sensors'][sensorType][id]["module"]]
        function = json['sensors'][sensorType][id]["function"]["name"]

        if (json['sensors'][sensorType][id]["testmode"]):
            value = {}
            tmpValue = ""
            for key in json['sensors'][sensorType][id]["values"].keys():
                testfile = json['sensors'][sensorType][id]["values"][key]["testfile"]
                #print(testfile)
                if os.path.isfile(testfile):
                    with open(testfile) as f:
                        firstline = f.readline().rstrip()
                    f.close
                else:
                    firstline = "-999"
                value[key] = float(firstline)
        else:
            # construct function call
            evalString = ("tempModule.%s" % function)
            params = json['sensors'][sensorType][id]["function"]["parameters"]

            if params:
                evalString += "("
                paramKeys = params.keys()
                count = 0
                paramsAmount = len(paramKeys)
                for key in paramKeys:
                    count += 1
                    value = json['sensors'][sensorType][id]["function"]["parameters"][key]
                    evalString += '"' + value + '"'
                    if count < paramsAmount:
                        evalString += ", "

            if params:
                evalString += ")"

            value = eval(evalString)
    return value

# endregion


# region variables
script = PHTCstandard.script_infos()
jsonfile = script["root"] + "/" + script["name"] + ".json"
global json
json = PHTCjson.readJson(jsonfile)
# Zählweise der Pins festlegen
GPIO.setmode(GPIO.BOARD)
# endregion

GPIO.setwarnings(False)

PHTCjson.updateJson1Wire(jsonfile, json)

global module
module = {}

# initialize GPIOs
for actuator in json["actuators"].keys():
    gpio = json["actuators"][actuator]["gpio"]
    GPIO.setup(gpio, GPIO.OUT)

# import needed modules
for sensorType in list(json['sensors'].keys()):
    for id in list(json['sensors'][sensorType].keys()):
        if id == "_comment":
            continue
        modulename = "modules." + json['sensors'][sensorType][id]["module"]
        if modulename not in sys.modules:
            module[json['sensors'][sensorType][id]
                   ["module"]] = dynamic_import(modulename)
        # print(getValue(id))


# print(eval(evalString))


#tempModule = module["ds18b20"]
#evalString = "tempModule.GetValue('28-01205f136d8b')"
# print(eval(evalString))


# print(module["ds18b20"].GetValue("28-01205f136d8b"))
# print(module["28-01205f136d8b"]("28-01205f136d8b"))


#print(eval("getValue('28-01205f136d8b', 'dummmy')"))

while True:
    for sensorType in list(json['sensors'].keys()):
        for id in list(json['sensors'][sensorType].keys()):
            if id == "_comment":
                continue

            tempModule = module[json['sensors'][sensorType][id]["module"]]
            function = json['sensors'][sensorType][id]["function"]["name"]

            minValue = False
            maxValue = False

            value = getSensorValues(sensorType, id)
            if value == False:
                print("Fehler beim Auslesen des Sensors")
                continue

            print("{} ({}):\tTemperatur: {}\tLuftfeuchtigkeit: {}".format(
                id, json['sensors'][sensorType][id]["description"], Round(value["temperature"], 2), value["humidity"]))

            if len(json['sensors'][sensorType][id]["values"].keys()) > 0:
                for valueKey in json['sensors'][sensorType][id]["values"].keys():
                    if len(json['sensors'][sensorType][id]["values"][valueKey]) > 0:
                        if "max" in json['sensors'][sensorType][id]["values"][valueKey].keys():
                            if "actuator" in json['sensors'][sensorType][id]["values"][valueKey]["max"]:
                                actuatorName = json['sensors'][sensorType][id]["values"][valueKey]["max"]["actuator"]
                                if actuatorName in json['actuators'] and "gpio" in json['actuators'][actuatorName].keys():
                                    actuatorGpio = json['actuators'][actuatorName]["gpio"]
                                    if "value" in json['sensors'][sensorType][id]["values"][valueKey]["max"]:
                                        maxValue = json['sensors'][sensorType][id]["values"][valueKey]["max"]["value"]
                                        if "referenceValue" in json['sensors'][sensorType][id]["values"][valueKey]["max"]:
                                            referenceSensorType = json['sensors'][sensorType][id]["values"][valueKey]["max"]["referenceValue"]["sensor"]["type"]
                                            referenceSensorId = json['sensors'][sensorType][id]["values"][valueKey]["max"]["referenceValue"]["sensor"]["id"]
                                            referenceSensorValueName = json['sensors'][sensorType][id]["values"][valueKey]["max"]["referenceValue"]["sensor"]["value"]
                                            referenceIf = json['sensors'][sensorType][id]["values"][valueKey]["max"]["referenceValue"]["if"]
                                            referenceValue = getSensorValues(referenceSensorType, referenceSensorId)
                                            if not referenceValue == False:
                                                referenceValue = referenceValue[referenceSensorValueName]
                                                if referenceIf == "lower":
                                                    if value[valueKey] > maxValue and referenceValue < value[valueKey]:
                                                        GPIO.output(actuatorGpio, GPIO.HIGH)
                                                    else:
                                                        GPIO.output(actuatorGpio, GPIO.LOW)
                                                        #print("{}:\tmax (lower)\t{}\tLOW".format(id, value))
                                                elif referenceIf == "higher":
                                                    if value[valueKey] > maxValue and referenceValue > value[valueKey]:
                                                        GPIO.output(actuatorGpio, GPIO.HIGH)
                                                    else:
                                                        GPIO.output(actuatorGpio, GPIO.LOW)
                                                        #print("{}:\tmax (higher)\t{}\tLOW".format(id, value))
                                        else:
                                            if value[valueKey] > maxValue:
                                                GPIO.output(actuatorGpio, GPIO.HIGH)
                                            else:
                                                GPIO.output(actuatorGpio, GPIO.LOW)

                        if "min" in json['sensors'][sensorType][id]["values"][valueKey].keys():
                            if "actuator" in json['sensors'][sensorType][id]["values"][valueKey]["min"]:
                                actuatorName = json['sensors'][sensorType][id]["values"][valueKey]["min"]["actuator"]
                                if actuatorName in json['actuators'] and "gpio" in json['actuators'][actuatorName].keys():
                                    actuatorGpio = json['actuators'][actuatorName]["gpio"]
                                    if "value" in json['sensors'][sensorType][id]["values"][valueKey]["min"]:
                                        minValue = json['sensors'][sensorType][id]["values"][valueKey]["min"]["value"]
                                        if "referenceValue" in json['sensors'][sensorType][id]["values"][valueKey]["min"]:
                                            referenceSensorType = json['sensors'][sensorType][id]["values"][valueKey]["min"]["referenceValue"]["sensor"]["type"]
                                            referenceSensorId = json['sensors'][sensorType][id]["values"][valueKey]["min"]["referenceValue"]["sensor"]["id"]
                                            referenceSensorValueName = json['sensors'][sensorType][id]["values"][valueKey]["min"]["referenceValue"]["sensor"]["value"]
                                            referenceIf = json['sensors'][sensorType][id]["values"][valueKey]["min"]["referenceValue"]["if"]
                                            referenceValue = getSensorValues(referenceSensorType, referenceSensorId)
                                            if not referenceValue == False:
                                                referenceValue = referenceValue[referenceSensorValueName]
                                                if referenceIf == "lower":
                                                    if value[valueKey] < minValue and referenceValue < value[valueKey]:
                                                        GPIO.output(actuatorGpio, GPIO.HIGH)
                                                        #print("{}:\tmin (lower)\t{}\tHIGH".format(id, value))
                                                    else:
                                                        GPIO.output(actuatorGpio, GPIO.LOW)
                                                        #print("{}:\tmin (lower)\t{}\tLOW".format(id, value))
                                                elif referenceIf == "higher":
                                                    if value[valueKey] < minValue and referenceValue > value[valueKey]:
                                                        GPIO.output(actuatorGpio, GPIO.HIGH)
                                                        #print("{}:\tmin (higher)\t{}\tHIGH".format(id, value))
                                                    else:
                                                        GPIO.output(actuatorGpio, GPIO.LOW)
                                                        #print("{}:\tmin (higher)\t{}\tLOW".format(id, value))
                                        else:
                                            if value[valueKey] < minValue:
                                                GPIO.output(actuatorGpio, GPIO.HIGH)
                                                #print("{}:\tmin\t{}\tHIGH".format(id, value))
                                            else:
                                                GPIO.output(actuatorGpio, GPIO.LOW)
                                                #print("{}:\tmin\t{}\tLOW".format(id, value))

    time.sleep(15)

GPIO.cleanup()
