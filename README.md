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

Controls a dehumidifier dynamically using physically sound decision logic instead of fixed thresholds.

**Features:**
- Compares indoor and outdoor absolute humidity: if ventilating would be more efficient, the dehumidifier stays off
- Considers outdoor temperature: no ventilation recommendation if it would overheat the apartment
- Optional minimum AH differential: dehumidifier only runs when indoor air is significantly more humid than outdoor
- Optional window/door sensors: dehumidifier turns off automatically when a window is opened
- Optional presence detection: when nobody is home, ventilation is ignored and the dehumidifier takes over
- Compressor protection via configurable minimum off time
- Emergency override at critical indoor humidity (mold protection)
- Hysteresis prevents rapid cycling
- Optional active time window

**Requirements:**
- Home Assistant 2024.6 or newer
- Indoor relative humidity sensor (required)
- Indoor absolute humidity sensor (required)
- Outdoor sensors optional (absolute humidity + temperature)

[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Spegeli/homeassistant-blueprints/main/climate/dehumidifier_control.yaml)

---

## Installation

1. Click the **"Import Blueprint"** button on the desired blueprint
2. Confirm in the Home Assistant dialog
3. Create an automation based on the blueprint and assign your sensors and devices
