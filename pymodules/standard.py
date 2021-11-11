#!/usr/bin/env python
#coding: utf8

def script_infos():
    import sys
    import os
    result = {
        "fullpath": sys.argv[0],
        "root": os.path.dirname(sys.argv[0]),
        "name": ((os.path.basename(sys.argv[0])).split("."))[0],
        "ext": (os.path.splitext(sys.argv[0]))[1],
        "nameext": os.path.basename(sys.argv[0])
    }
    return result
    