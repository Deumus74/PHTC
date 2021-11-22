#!/usr/bin/env python
# coding: utf8

def GetValue(id):
    import os
    import re
    valueFile = ("/sys/bus/w1/devices/%s/w1_slave" % id)
    if os.path.isfile(valueFile):
        #print("gefunden: %s" % valueFile)
        with open(valueFile, 'r') as openfile:
            value = (openfile.read()).strip()
            openfile.close
        # check CRC
        if re.search(r"crc=\S\S+\s(.*?)\s", value).group(1) == "YES":
            # check temperature
            temperatureString = re.search(r"t=(.*?)$", value).group(1)
            result = float(("%s.%s" % (temperatureString[:len(
                temperatureString) - 3], temperatureString[-3:])))
        else:
            result = False
    else:
        #print("nicht gefunden: %s" % valueFile)
        result = False

    return result
