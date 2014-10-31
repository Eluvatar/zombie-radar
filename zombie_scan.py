#!/usr/bin/python2.7
from parser.api import request as api_request
from time import struct_time
def scan_nation(nat):
    entry = {"name":nat}
    natxml = api_request({'nation':nat,'q':'zombie'})
    entry = parse_nation(natxml)
    entry["name"] = nat
    return entry

def parse_nation(natxml):
    entry = dict()
    entry["ts"] = struct_time(natxml.headers.getdate('Date'))
    zx = natxml.find('ZOMBIE')
    entry["action"] = zx.find('ZACTION').text
    entry["zombies"] = int(zx.find('ZOMBIES').text)
    entry["survivors"] = int(zx.find('SURVIVORS').text)
    entry["dead"] = int(zx.find('DEAD').text)
    return entry
