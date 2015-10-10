#   Simple module to track happenings that change the zombie levels
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

from transmission.reception import subscribe
import time, threading
from zombie_scan import scan_nation

db = dict()
dblock = threading.Lock()

def on_entry_change(entry):
    pass

def handle_event(entry_delta):
    nat = entry_delta["name"]
    with dblock:
        if nat not in db:
            return
        entry = db[nat]
    last_update = entry["ts"]
    event_ts = entry_delta["ts"]
    if( event_ts.tm_hour > last_update.tm_hour 
        or (event_ts.tm_hour == 0 and last_update.tm_hour != 0) ):
        entry = scan_nation(nat)
        with dblock:
            db[nat] = entry
        return
    if( event_ts < last_update ):
        return
    entry["ts"] = event_ts
    for key in ("zombies","survivors","dead"):
        if key in entry_delta:
            entry[key] += entry_delta[key]
    on_entry_change(entry)

@subscribe(pattern='@@(nation)@@ was struck by a Cure Missile from @@nation@@, curing (\d+) million infected.')
def handle_cure_missile(event):
    nat = event.group(1)
    n = int(event.group(2))
    entry_delta = {'name':nat,'ts':time.gmtime(event.timestamp),'zombies':-n,'survivors':+n}
    handle_event(entry_delta)

@subscribe(pattern='@@(nation)@@ was ravaged by a Zombie Horde from @@nation@@, infecting (\d+) million survivors.')
def handle_zombie_horde(event):
    nat = event.group(1)
    n = int(event.group(2))
    entry_delta = {'name':nat,'ts':time.gmtime(event.timestamp),'zombies':+n,'survivors':-n}
    handle_event(entry_delta)

@subscribe(pattern='@@(nation)@@ was cleansed by a Tactical Zombie Elimination Squad from @@nation@@, killing (\d+) million zombies.')
def handle_zombie_elimination(event):
    nat = event.group(1)
    n = int(event.group(2))
    entry_delta = {'name':nat,'ts':time.gmtime(event.timestamp),'zombies':-n,'dead':+n}
    handle_event(entry_delta)


