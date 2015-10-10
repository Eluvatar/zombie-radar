#!/usr/bin/python2.7
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

"""
Driver which takes command line input and uses transmission (and trawler) to
collect and update zombie data, and serve it through a simple HTTP JSON API
"""

import argparse

parser = argparse.ArgumentParser(description="Observe zombies")
parser.add_argument('regions', metavar="reg", type=str, nargs='+', help='a region to watch')
parser.add_argument('-u','--user', required=True, help='a nation name, email, or web page to identify the user as per item 1 of the NS API Terms of Use: http://www.nationstates.net/pages/api.html#terms')
parser.add_argument('-p','--port', default=6264, type=int, help='an [unprivileged: 1024 to 65536] port number for the runner to display its data through (default=6264)')
parser.add_argument('-v','--verbose', action='store_true') 

args = parser.parse_args()

import parser.api as api
api.user_agent = "Zombie Radar ({0})".format(args.user)

import urllib2, urllib, json, threading, copy, time
from datetime import datetime
import os.path
import zombie_scan, zombie_init
from ns import id_str

region_names = frozenset(map(id_str, args.regions))

import inspect

class VerboseLock(object):
    def __init__(self, name):
        self.lock = threading.Lock()
        self.name = name
    
    def __enter__(self):
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %Z")
        print "{0} - acquiring {3} for {1} (line {2})".format(ts, caller.function, caller.lineno, self.name)
        self.lock.acquire()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %Z")
        print "{0} - acquired {3} for {1} (line {2})".format(ts, caller.function, caller.lineno, self.name)
     
    def __exit__(self, type, value, traceback):
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %Z")
        print "{0} - releasing {3} for {1} (line {2})".format(ts, caller.function, caller.lineno, self.name)
        self.lock.release()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %Z")
        print "{0} - released {3} for {1} (line {2})".format(ts, caller.function, caller.lineno, self.name)

if args.verbose:
    dblock = VerboseLock('dblock')
else:
    dblock = threading.Lock()

regions = dict()
rlocks = dict()
rcache = dict()

if args.verbose:
    for name in region_names:
        regions[name] = set(api.request({'q':'nations','region':name}).find('NATIONS').text.split(':'))
        rlocks[name] = VerboseLock("region."+name)
else:
    for name in region_names:
        regions[name] = set(api.request({'q':'nations','region':name}).find('NATIONS').text.split(':'))
        rlocks[name] = threading.Lock()

from calendar import timegm
def save():
    with dblock:
        db_copy = copy.deepcopy(db)
    for nat in db_copy:
        if "ts" in db_copy[nat]:
            ts = timegm(db_copy[nat]["ts"])
            db_copy[nat]["ts"] = ts
    json.dump(db_copy,open("zombies.json","w"))

if os.path.isfile("zombies.json"):
    db = json.load(open('zombies.json','r'))
    hour_ago = time.gmtime(time.time()-3600)
    for nat in db:
        if "ts" in db[nat]:
            db[nat]["ts"] = time.gmtime(db[nat]["ts"])
        else:
            db[nat]["ts"] = hour_ago
    zcloak = False
    for nat in set.union(*regions.values()) - frozenset(db.keys()):
        if not zcloak:
            try:
                entry = zombie_scan.scan_nation(nat)
            except zombie_scan.ZombiesCloaked:
                zcloak = True
                entry = zombie_init.init_nation(nat)
        else:
            entry = zombie_init.init_nation(nat)
        db[nat] = entry
else:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %Z")
    print "{0} Initializing zombie data for the regions {1} (this may take a while: printing a . for every 100 nations processed, including nations in other regions skipped)".format(ts, list(region_names))
    db = zombie_init.initialize_nations(set.union(*regions.values()))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %Z")
    print "{0} Initialized zombie data, saving to zombies.json".format(ts)
    save()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %Z")
    print "{0} Saved initial zombie data to zombies.json".format(ts)

def on_arrival(reg, nat):
    if reg in region_names:
        with rlocks[reg]:
            regions[reg].add(nat)
            try:
                entry = zombie_scan.scan_nation(nat)
            except zombie_scan.ZombiesCloaked:
                entry = zombie_init.init_nation(nat)
            with dblock:
                db[nat] = entry
        rcache.pop(reg, None)

def on_departure(reg, nat):
    if reg in region_names:
        with rlocks[reg]:
            regions[reg].discard(nat)
        rcache.pop(reg, None)

import location_monitor
location_monitor.on_arrival = on_arrival
location_monitor.on_departure = on_departure

class Locks(object):
    def __init__(self, locks):
        self.locks = locks
    
    def __enter__(self):
        for lock in self.locks:
            lock.acquire()
    
    def __exit__(self):
        for lock in self.locks:
            lock.release()

def on_entry_change(entry):
    nat = entry['name']
    with Locks(rlocks.values()):
        if nat in set.union(*regions.values()):
            with dblock:
                if "action" in db[nat] and "action" not in entry:
                    entry["action"] = db[nat]["action"]
                db[nat]=entry
                for reg in region_names:
                    if nat in regions[reg]:
                        rcache.pop(reg, None)

def get_stack():
    with dblock:
        entries = copy.deepcopy(db.values())
    nats = map(lambda e: id_str(e['name']), entries)
    populations = map(lambda e: e['zombies']+e['survivors']+e['dead'], entries)
    _q = zip(populations, nats)
    _q.sort()
    return map(lambda q: q[1], _q)

import zombiedar
zombiedar.on_entry_change = on_entry_change
zombiedar.db = db
zombiedar.dblock = dblock

from time import sleep
def radar_loop():
    last_cycle = time.gmtime().tm_hour-1
    while True:
        start = time.gmtime()
        now = start 
        stack = get_stack()
        while( len(stack) > 0 and start.tm_hour == now.tm_hour ):
            nat = stack.pop()
            with dblock:
                while db[nat]["ts"].tm_hour == start.tm_hour:
                    nat = stack.pop()
            try: 
                entry = zombie_scan.scan_nation(nat)
                with dblock:
                    db[nat] = entry
                    for reg in region_names:
                        if nat in regions[reg]:
                            rcache.pop(reg, None)
            except api.CTE:
                with dblock:
                    del db[nat]
                pass
            except:
                print "Exception on nation {0}".format(nat)
                raise
            save()
            now = time.gmtime()
        if now.tm_hour == start.tm_hour:
            next_hour = time.gmtime(timegm(now)+3600)
            next_hour = time.struct_time((next_hour.tm_year, next_hour.tm_mon, next_hour.tm_mday, next_hour.tm_hour, 0, 0, next_hour.tm_wday, next_hour.tm_yday, next_hour.tm_isdst))
            tosleep = time.mktime(next_hour) - time.time()
            sleep(tosleep)


import cherrypy
JSON = 'application/json; charset=utf-8'

class ZombieRadarServer(object):
    exposed = True
   
    @cherrypy.expose 
    def default(self, *args, **params):
        cherrypy.response.headers['Content-Type']=JSON
        if( len(args) != 1 or len(params) != 0 ):
            cherrypy.response.status = 400
            return ''
        region = id_str(args[0])
        if( region not in region_names ):
            cherrypy.response.status = 404
            return '[]'
        return self.region_api(region)
    
    def region_api(self, region):
        cherrypy.response.headers['Access-Control-Allow-Origin']= "*"
        with rlocks[region]:
            rjson = rcache.get(region)
            if rjson is None:
                res = list()
                with dblock:
                    for nat in regions[region]:
                        entry = copy.deepcopy(db[nat])
                        entry["ts"] = timegm(entry["ts"])
                        res.append(entry)
                rjson = json.dumps(res)
                rcache[region] = rjson
            return rjson

worker = threading.Thread(target=radar_loop)
worker.start()

conf = {
    'global':{
        'server.socket_host':'0.0.0.0',
        'server.socket_port':args.port,
        'tools.gzip.on': True,
    }
}
cherrypy.quickstart(ZombieRadarServer(),'/',conf)
