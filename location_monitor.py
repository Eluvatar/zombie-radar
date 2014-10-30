from transmission.reception import subscribe

def on_departure(reg, nat):
    pass

def on_arrival(reg, nat):
    pass

def on_founded(nat):
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
    nat = event.group(1)
    reg = event.group(2)
    entry = {"name":nat}
    on_founded(nat)
    handle_event(nat, None, reg)
