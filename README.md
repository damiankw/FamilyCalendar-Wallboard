# FamilyCalendar Wallboard – Screen Scheduler

An autonomous screen scheduler for a Raspberry Pi-based family calendar wallboard. The service automatically turns an HDMI display on and off according to a configurable daily schedule, and allows a physical GPIO button to temporarily override the schedule and switch the screen on.

---

## Features

- **Time-based schedule** – Define as many on/off time slots per day as you need.
- **GPIO button override** – Press a physical button to turn the screen on for a configurable number of minutes, regardless of the current schedule.
- **Wayland-native** – Uses [`wlr-randr`](https://sr.ht/~emersion/wlr-randr/) to control the display output, making it compatible with Raspberry Pi OS running a Wayland compositor (e.g. Wayfire or labwc).
- **Systemd service** – Runs automatically on boot, restarts on failure, and integrates cleanly with the system.

---

## Requirements

- Raspberry Pi running a Wayland-based desktop (e.g. Raspberry Pi OS Bookworm with Wayfire)
- Python 3
- [`wlr-randr`](https://sr.ht/~emersion/wlr-randr/) installed and accessible on `$PATH`
- [`gpiozero`](https://gpiozero.readthedocs.io/) Python library (pre-installed on Raspberry Pi OS)
- A physical button wired between a GPIO pin and ground (optional, but required for override functionality)

---

## Installation

The included `install.sh` script handles all installation steps automatically. It must be run with `sudo`.

```bash
sudo bash install.sh
```

The script will:

1. Create the configuration directory `/etc/screen-scheduler/`.
2. Copy `screen_scheduler.py` to `/usr/local/bin/`.
3. Install the `screen-scheduler.service` systemd unit file.
4. Write a default `config.json` to `/etc/screen-scheduler/config.json` (only if one does not already exist).
5. Enable and start the `screen-scheduler` systemd service.

---

## Configuration

The configuration file is located at `/etc/screen-scheduler/config.json`.

```json
{
  "output_name": "HDMI-A-1",
  "button_gpio": 17,
  "override_minutes": 30,
  "scheduler_interval": 15,
  "schedule": [
    ["06:00", "on"],
    ["10:00", "off"],
    ["17:00", "on"],
    ["19:00", "off"]
  ]
}
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `output_name` | string | `"HDMI-A-1"` | The `wlr-randr` output name for the display to control. Run `wlr-randr` with no arguments to list available outputs. |
| `button_gpio` | integer | `17` | BCM GPIO pin number that the physical override button is connected to. The pin is configured with an internal pull-up resistor; connect the button between this pin and ground. |
| `override_minutes` | integer | `30` | How many minutes the screen stays on after the override button is pressed. |
| `scheduler_interval` | integer | `15` | How often (in seconds) the scheduler checks whether the screen state needs to change. |
| `schedule` | array | see above | An ordered list of `["HH:MM", "on"/"off"]` pairs. At any given time the scheduler uses the **last entry whose time has passed** to determine whether the screen should be on or off. Entries should be in chronological order. |

After editing the configuration file, restart the service for changes to take effect:

```bash
sudo systemctl restart screen-scheduler
```

---

## How It Works

1. **Scheduler loop** – Every `scheduler_interval` seconds the script evaluates the current time against the `schedule` list. It walks through all schedule entries and applies the last one whose time is ≤ the current time of day. If the resulting state is `"on"`, the screen is turned on; otherwise it is turned off.

2. **Button override** – A `gpiozero.Button` listener runs in the background on the configured GPIO pin. When the button is pressed, the screen is immediately turned on and an override timer is set (`override_minutes` from now). While the override is active the scheduler will not turn the screen off, even if the schedule says it should be off.

3. **Display control** – Screen state is changed by calling `wlr-randr --output <output_name> --on` or `--off`. The script tracks the current state and avoids issuing redundant commands.

---

## Service Management

| Task | Command |
|------|---------|
| Check service status | `sudo systemctl status screen-scheduler` |
| View live logs | `sudo journalctl -u screen-scheduler -f` |
| Stop the service | `sudo systemctl stop screen-scheduler` |
| Start the service | `sudo systemctl start screen-scheduler` |
| Restart after config change | `sudo systemctl restart screen-scheduler` |
| Disable auto-start on boot | `sudo systemctl disable screen-scheduler` |

---

## File Overview

| File | Description |
|------|-------------|
| `screen_scheduler.py` | Main Python script – schedule logic, GPIO handling, display control |
| `config.json` | Example / default configuration file |
| `screen-scheduler.service` | systemd unit file |
| `install.sh` | Installation script |
