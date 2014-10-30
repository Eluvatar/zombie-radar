#!/usr/bin/python2.7
from parser.api import request as api_request
from time import struct_time
def scan_nation(nat):
    try:
        entry = {"name":nat}
        natxml = api_request({'nation':nat,'q':'zombie'})
        entry["ts"] = struct_time(natxml.headers.getdate('Date'))
        zx = natxml.find('ZOMBIE')
        entry["action"] = zx.find('ZACTION').text
        entry["zombies"] = int(zx.find('ZOMBIES').text)
        entry["survivors"] = int(zx.find('SURVIVORS').text)
        entry["dead"] = int(zx.find('DEAD').text)
        res.append(entry)
    except:
        pass
    return entry
