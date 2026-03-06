#!/usr/bin/env python3
"""
Autonomous Screen Scheduler for Raspberry Pi
- Handles scheduled ON/OFF times
- Monitors GPIO button for temporary override
- Reads configuration from /etc/screen-scheduler/config.json
"""

import json
import subprocess
import time
import threading
from datetime import datetime, timedelta
from gpiozero import Button

# -------------------------
# CONFIG
# -------------------------

CONFIG_FILE = "/etc/screen-scheduler/config.json"

with open(CONFIG_FILE) as f:
    config = json.load(f)

OUTPUT_NAME = config.get("output_name", "HDMI-A-1")
BUTTON_GPIO = config.get("button_gpio", 17)
BUTTON_OVERRIDE_MINUTES = config.get("override_minutes", 30)
SCHEDULER_INTERVAL = config.get("scheduler_interval", 15)
SCHEDULE = config.get("schedule", [["06:00","on"],["10:00","off"]])

# -------------------------
# STATE
# -------------------------

screen_on_state = False
override_until = None

# -------------------------
# SCREEN CONTROL
# -------------------------

def screen_on():
    global screen_on_state
    if not screen_on_state:
        subprocess.run(["wlr-randr", "--output", OUTPUT_NAME, "--on"])
        screen_on_state = True

def screen_off():
    global screen_on_state
    if screen_on_state:
        subprocess.run(["wlr-randr", "--output", OUTPUT_NAME, "--off"])
        screen_on_state = False

# -------------------------
# SCHEDULE CHECK
# -------------------------

def schedule_should_be_on():
    now = datetime.now().time()
    last_state = "off"
    for time_str, state in SCHEDULE:
        t = datetime.strptime(time_str, "%H:%M").time()
        if now >= t:
            last_state = state
    return last_state == "on"

# -------------------------
# BUTTON HANDLER
# -------------------------

def button_pressed():
    global override_until
    override_until = datetime.now() + timedelta(minutes=BUTTON_OVERRIDE_MINUTES)
    screen_on()

# -------------------------
# SCHEDULER LOOP
# -------------------------

def scheduler_loop():
    global override_until
    while True:
        now = datetime.now()
        scheduled_on = schedule_should_be_on()
        override_active = override_until and now < override_until

        if scheduled_on or override_active:
            screen_on()
        else:
            screen_off()

        time.sleep(SCHEDULER_INTERVAL)

# -------------------------
# MAIN
# -------------------------

button = Button(BUTTON_GPIO, pull_up=True, bounce_time=0.2)
button.when_pressed = button_pressed

threading.Thread(target=scheduler_loop, daemon=True).start()

# keep main thread alive
while True:
    time.sleep(60)
