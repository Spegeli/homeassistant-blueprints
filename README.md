# Home Assistant Blueprints

A collection of Home Assistant blueprints for automations.

---

## Categories

| Folder | Description |
|---|---|
| [`climate/`](./climate) | Temperature, humidity, dehumidifiers, heating, air conditioning |
| [`lighting/`](./lighting) | Light automations and scenes |
| [`security/`](./security) | Alarms, locks, cameras |
| [`presence/`](./presence) | Presence detection, arrival/departure routines |
| [`energy/`](./energy) | Power consumption, solar, load management |
| [`notifications/`](./notifications) | Alerts and reminders |

---

## Blueprints

### 🌡 Climate

#### Smart Dehumidifier Control

Controls a dehumidifier with your own room sensor instead of the device's built-in hygrostat, and tells you when opening a window would dry the room better.

**Features:**
- Turns on above the target humidity and off below the turn-off threshold, with an emergency override at critical humidity (mold protection)
- Compares indoor and outdoor air via the dew point: recommends ventilation when the outdoor air, warmed to room temperature, would be noticeably drier
- No ventilation recommendation if it would heat the room above your comfort temperature or cool it down too much
- Optional actions (e.g. notifications): "please ventilate" and "close the window", with a ventilation time based on the outdoor temperature
- If nobody ventilates in time, the dehumidifier takes over
- Optional window/door sensors: the dehumidifier turns off while a window is open
- Optional presence detection: ventilation is only recommended while someone is home
- Compressor protection with minimum run and off times
- Optional active time window and override of the device's own hygrostat

**Requirements:**
- Home Assistant 2024.8 or newer
- Indoor relative humidity sensor (required)
- For ventilation recommendations: indoor temperature, outdoor temperature and outdoor humidity sensors (a weather service is fine)

How it decides, with 50 calculated scenarios: [dehumidifier_control.md](climate/dehumidifier_control.md)

[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Spegeli/homeassistant-blueprints/main/climate/dehumidifier_control.yaml)

---

### 👤 Presence

#### Person Arrival & Departure Automation

Trigger actions when a specific person arrives home or leaves home.

**Features:**
- Separate actions configurable for arrival and departure
- Works with any Home Assistant person entity

[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Spegeli/homeassistant-blueprints/main/presence/person_presence.yaml)

---

## Installation

1. Click the **"Import Blueprint"** button on the desired blueprint
2. Confirm in the Home Assistant dialog
3. Create an automation based on the blueprint and assign your sensors and devices

---

## Contributing

Bug reports, ideas and pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.
