#!/usr/bin/env python
#coding: utf8

#Plants Hibernation Tent Control

# region Imports
import sys
import os
import json
from pymodules import standard
# endregion

# region Funktionen

# endregion

# region Variablen
script = standard.script_infos()
jsonfile = script["root"] + "/" + script["name"] + ".json"
# endregion

print(jsonfile)
print(script)
