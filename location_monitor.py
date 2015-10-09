#   Simple module to track the location of nations
#   Copyright (C) 2013-2015 Eluvatar
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

def on_departure(reg, nat):
    pass

def on_arrival(reg, nat):
    pass

def on_founded(nat):
    pass

def on_refounded(nat):
    pass

def handle_event(nat, reg_from, reg_to):
    on_departure(reg_from, nat)
    on_arrival(reg_to, nat)

@subscribe(pattern="@@(nation)@@ relocated from %%(region)%% to %%(region)%%.")
def handle_movement(event):
    nat = event.group(1)
    reg_from = event.group(2)
    reg_to = event.group(3)
    handle_event(nat, reg_from, reg_to)

@subscribe(pattern="@@(nation)@@ was founded in %%(region)%%.")
def handle_founded(event):
    _handle_founded(event)

@subscribe(pattern="@@(nation)@@ was refounded in %%(region)%%.")
    _handle_founded(event)

def _handle_founded(event):
    nat = event.group(1)
    reg = event.group(2)
    entry = {"name":nat}
    on_founded(nat)
    handle_event(nat, None, reg)
