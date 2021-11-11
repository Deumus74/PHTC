#!/usr/bin/python3
# -*- coding: utf-8 -*-

# TODO: Script-Beschreibung erstellen
# Systempfad zum den Sensor, weitere Systempfade könnten über ein Array
# oder weiteren Variablen hier hinzugefügt werden.
# 28-02161f5a48ee müsst ihr durch die eures Sensors ersetzen!
# 28-01205f136d8b  28-01205f3d587e
# sudo apt-get install python3-w1thermsensor

# region functions
def GetValue_W1ThermSensor():
    global module
    global id
    value = module.W1ThermSensor(sensor_id=id).get_temperature()
    return value

# enregion
#

# Variablen
# TODO: Variablen über ini-Datei einlesen

#import w1thermsensor
import sys
import importlib
import json

#import w1thermsensor
#from w1thermsensor import W1ThermSensor
from pymodules import standard

script = standard.script_infos()
jsonfile = script["root"] + "/" + "PHTC.json"

# Opening JSON file
f = open(jsonfile,)

# returns JSON object as a dictionary
json = json.load(f)
#port = json["tcp"]["port"]

sensors = json["sensors"]
sensorModule = {}

# load needed modules for sensors
for sensor in sensors:
    if "module" in json["sensors"][sensor]:
        sensorModulename = json["sensors"][sensor]["module"]
        if sensorModulename.lower() not in sys.modules:
            print("Modul " + sensorModulename + " nicht geladen")
            sensorModule[sensorModulename] = importlib.import_module(sensorModulename)
        else:
            print("Modul " + sensorModulename + " bereits geladen")

module = sensorModule["w1thermsensor"]
id = "01205f3d587e"

function = (json["modules"]["w1thermsensor"]["functions"]["get-value"])
print(function)
print(locals()[function]())
print(globals()[function]())
#CallFunction(function)
#GetValue(sensorModule["w1thermsensor"], "01205f3d587e")

print("huhu")
"""
tempsensors = {
    '01205f136d8b': "aussen",
    '01205f3d587e': "innen"}


thermtyp = "THERM_SENSOR_DS18B20"
# , tempsensors["aussen"])
#sensortyp = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20)
sensors = W1ThermSensor().get_available_sensors()
#print(sensortyp)
#sensors = sensortyp.get_available_sensors()
print(sensors)



for sensor in sensors:
    if sensor.id in tempsensors:
        print(tempsensors[sensor.id])
    else:
        print(sensor.id)
    print(sensor.get_temperature())


# print(sensors[0].id)

# w1thermsensor.W1ThermSensor.


global w1syspath
w1syspath = '/sys/bus/w1/devices/'
tempsensors = ['28-01205f136d8b/w1_slave', '28-01205f3d587e/w1_slave']
 
def read_ds18b20(sensorName):
    #TODO: Funktionsbeschreibung erstellen
    f = open(w1syspath + sensorName, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temerature(sensorName):
    line = read_ds18b20(sensorName)
    temp = 
    return line

print(read_temerature(tempsensors[0]))
"""
