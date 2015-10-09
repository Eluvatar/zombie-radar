#!/usr/bin/python2.7
#   Simple module to scan a nation for zombies
#   Copyright (C) 2013-2014 Eluvatar
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
