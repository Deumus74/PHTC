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
import logging
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

#logging
timeStamp = time.strftime('%Y-%m-%d', time.localtime())
logDir = script["root"] + "/log"
logFile = logDir + "/" + timeStamp + ".log"
logging.basicConfig(filename=logFile, level=logging.DEBUG,
                    format='%(asctime)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

#json
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
logging.info("#### START SCRIPT ####")

try:
    logging.info("### set GPIOs to output ###")
    for actuator in json["actuators"].keys():
        for gpio in json["actuators"][actuator]["gpio"]:
            logging.info("gpio " + str(gpio))
            GPIO.setup(gpio, GPIO.OUT)
except Exception as e:
    logging.error('Error at %s', 'set GPIO.OUT', exc_info=e)

# import needed modules
try:
    logging.info("### import needed sensor modules ###")
    for sensorType in list(json['sensors'].keys()):
        logging.info("## sensor type " + sensorType + " ##")
        for id in list(json['sensors'][sensorType].keys()):
            if id == "_comment":
                continue
            logging.info("## sensor id: " + id + " ##")
            modulename = "modules." + json['sensors'][sensorType][id]["module"]
            if modulename not in sys.modules:
                logging.info("load module " + modulename)
                module[json['sensors'][sensorType][id]
                    ["module"]] = dynamic_import(modulename)
except Exception as e:
    logging.error('Error at %s', 'import sensor modules', exc_info=e)


try:
    logging.info("### Read sensors and switch actuators ###")
    for sensorType in list(json['sensors'].keys()):
        logging.info("## sensor type " + sensorType + " ##")

        for id in list(json['sensors'][sensorType].keys()):
            if id == "_comment":
                continue
            sensorDescription = json['sensors'][sensorType][id]['description']
            logging.info("# sensor " + sensorDescription + "(" + id + ") #")
            tempModule = module[json['sensors'][sensorType][id]["module"]]
            function = json['sensors'][sensorType][id]["function"]["name"]

            minValue = False
            maxValue = False

            value = getSensorValues(sensorType, id)
            if value == False:
                logging.error("Error when reading out the sensor")
                continue
            else:
                output = ""
                for item, val in value.items():
                    v = round(val, 2)
                    output += ("{} = {}".format(item, v)) + "  "
                logging.info("sensor values: " + output)

            if len(json['sensors'][sensorType][id]["values"].keys()) > 0:
                for valueKey in json['sensors'][sensorType][id]["values"].keys():
                    if len(json['sensors'][sensorType][id]["values"][valueKey]) > 0:
                        if "max" in json['sensors'][sensorType][id]["values"][valueKey].keys():
                            logging.info("# compare max values #")
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
                                                        for gpio in actuatorGpio:
                                                            logging.info("switch on: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                            GPIO.output(gpio, GPIO.HIGH)
                                                    else:
                                                        for gpio in actuatorGpio:
                                                            logging.info("switch off: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                            GPIO.output(gpio, GPIO.LOW)
                                                elif referenceIf == "higher":
                                                    if value[valueKey] > maxValue and referenceValue > value[valueKey]:
                                                        for gpio in actuatorGpio:
                                                            logging.info("switch on: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                            GPIO.output(gpio, GPIO.HIGH)
                                                    else:
                                                        for gpio in actuatorGpio:
                                                            logging.info("switch off: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                            GPIO.output(gpio, GPIO.LOW)
                                        else:
                                            if value[valueKey] > maxValue:
                                                for gpio in actuatorGpio:
                                                    logging.info("switch on: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                    GPIO.output(gpio, GPIO.HIGH)
                                            else:
                                                for gpio in actuatorGpio:
                                                    logging.info("switch off: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                    GPIO.output(gpio, GPIO.LOW)

                        if "min" in json['sensors'][sensorType][id]["values"][valueKey].keys():
                            logging.info("# compare min values #")
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
                                                        for gpio in actuatorGpio:
                                                            logging.info("switch on: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                            GPIO.output(gpio, GPIO.HIGH)
                                                    else:
                                                        for gpio in actuatorGpio:
                                                            logging.info("switch off: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                            GPIO.output(gpio, GPIO.LOW)
                                                elif referenceIf == "higher":
                                                    if value[valueKey] < minValue and referenceValue > value[valueKey]:
                                                        for gpio in actuatorGpio:
                                                            logging.info("switch on: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                            GPIO.output(gpio, GPIO.HIGH)
                                                    else:
                                                        for gpio in actuatorGpio:
                                                            logging.info("switch off: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                            GPIO.output(gpio, GPIO.LOW)
                                        else:
                                            if value[valueKey] < minValue:
                                                for gpio in actuatorGpio:
                                                    logging.info("switch on: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                    GPIO.output(gpio, GPIO.HIGH)
                                            else:
                                                for gpio in actuatorGpio:
                                                    logging.info("switch off: " + actuatorName + "(GPIO " + str(gpio) + ")")
                                                    GPIO.output(gpio, GPIO.LOW)
except Exception as e:
    logging.error('Error at %s', 'read sensors and switch actuators', exc_info=e)
