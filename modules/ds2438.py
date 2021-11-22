def GetValue(id):
    import os
    import re
    result = {
        "temperature": -999,
        "humidity": -999
    }
    temperatureFile = ("/sys/bus/w1/devices/%s/temperature" % id)
    humidityFile = ("/sys/bus/w1/devices/%s/vad" % id)

    try:
        if os.path.isfile(temperatureFile):
            #print("gefunden: %s" % temperatureFile)
            value = ""
            with open(temperatureFile, 'r') as openfile:
                tempValue = (openfile.read()).strip()
                openfile.close

            temperature = float(tempValue) / 256

            result["temperature"] = temperature
        else:
            print("nicht gefunden: %s" % temperatureFile)
            result["temperature"] = -999

        if os.path.isfile(humidityFile):
            value = ""
            with open(humidityFile, 'r') as openfile:
                value = (openfile.read()).strip()
                openfile.close
        
            result["humidity"] = float(value) / 10.0
    except: 
        result = False

    return result
