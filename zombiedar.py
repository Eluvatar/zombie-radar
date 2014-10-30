from transmission.reception import subscribe
import time
from zombie_scan import scan_nation

db = dict()

def on_entry_change(entry):
    pass

def handle_event(entry_delta):
    nat = entry_delta["name"]
    if nat not in db:
        return
    entry = db["nat"]
    last_update = time.gmtime(entry["ts"])
    event_ts = time.gmtime(entry_delta["ts"])
    if( event_ts.tm_hour > last_update.tm_hour 
        or (event_ts.tm_hour == 0 and last_update.tm_hour != 0) ):
        db[nat] = entry = scan_nation(nat)
        return
    if( event_ts < last_update ):
        return
    entry["ts"] = event_ts
    entry["action"] = entry_delta["action"]
    for key in ("zombies","survivors","dead"):
        if key in entry_delta:
            entry[key] += entry_delta[key]
    on_entry_change(entry)

@subscribe(pattern='@@(nation)@@ was struck by a Cure Missile from @@nation@@, curing (\d+) million infected.')
def handle_cure_missile(event):
    nat = event.group(1)
    n = event.group(2)
    entry_delta = {'name':nat,'ts':event.timestamp,'zombies':-n,'survivors':+n}
    handle_event(entry_delta)

@subscribe(pattern='@@(nation)@@ was ravaged by a Zombie Horde from @@nation@@, infecting (\d+) million survivors.')
def handle_zombie_horde(event):
    nat = event.group(1)
    n = event.group(2)
    entry_delta = {'name':nat,'ts':event.timestamp,'zombies':+n,'survivors':-n}
    handle_event(entry_delta)

@subscribe(pattern='@@(nation)@@ was cleansed by a Tactical Zombie Elimination Squad from @@nation@@, killing (\d+) million zombies.')
def handle_zombie_elimination(event):
    nat = event.group(1)
    n = event.group(2)
    entry_delta = {'name':nat,'ts':event.timestamp,'zombies':-n,'dead':+n}
    handle_event(entry_delta)


