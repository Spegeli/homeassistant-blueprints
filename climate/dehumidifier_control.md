# Smart Dehumidifier Control – how it decides

Background for [`dehumidifier_control.yaml`](dehumidifier_control.yaml) (version 3.0): the physics behind the decisions, the exact logic and 56 calculated scenarios.

- [1. Relative humidity, absolute humidity and dew point](#1-relative-humidity-absolute-humidity-and-dew-point)
- [2. When ventilation dries the room](#2-when-ventilation-dries-the-room)
- [3. Decision logic](#3-decision-logic)
- [4. Ventilating in practice](#4-ventilating-in-practice)
- [5. Mould and cold walls](#5-mould-and-cold-walls)
- [6. Dehumidifier efficiency](#6-dehumidifier-efficiency)
- [7. Scenarios](#7-scenarios)
- [8. Sources](#8-sources)

## 1. Relative humidity, absolute humidity and dew point

- **Relative humidity (RH, %)**: how much water the air holds compared with the maximum at its current temperature. Warm air can hold more water, so the same amount of water means a lower RH in warm air and a higher RH in cold air.
- **Absolute humidity (AH, g/m³)**: grams of water per cubic metre of air.
- **Dew point (Td, °C)**: the temperature at which the air would be saturated (100 % RH) and water starts to condense. It only depends on the amount of water, not on the air temperature.

Each measure answers a different question:

| Question | Measure | Why |
|---|---|---|
| Is the room too humid, should the dehumidifier run? | RH of the room air | Mould, bedding, sofas, clothes and wood take up water according to the RH of the air around them, not according to grams per m³. |
| Would ventilating dry the room? | Amount of water indoors vs. outdoors (dew point or AH) | Only the water content counts. The outdoor air changes its temperature, and with it its RH, once it is inside. |
| Will a cold wall get damp? | RH directly at the wall surface | Air cools down at a cold wall, so its RH rises there. |

The blueprint therefore switches the dehumidifier on the room RH and uses the water content only to decide whether ventilation is the better option. Absolute humidity sensors are not needed: the blueprint calculates everything from temperature and RH with the Magnus formula (over water, Sonntag 1990, valid from −45 to +60 °C):

```
e_s(T) = 6.112 · exp(17.62 · T / (243.12 + T))     saturation vapour pressure (hPa)
e      = RH / 100 · e_s(T)                          vapour pressure (hPa)
AH     = 216.7 · e / (273.15 + T)                   absolute humidity (g/m³)
γ      = ln(RH / 100) + 17.62 · T / (243.12 + T)
Td     = 243.12 · γ / (17.62 − γ)                   dew point (°C)
RH₂    = RH₁ · e_s(T₁) / e_s(T₂)                    the same air at another temperature
```

Absolute humidity and dew point of room air:

<!-- BEGIN dew-points -->
| Room | 45 % | 50 % | 55 % | 60 % | 65 % | 70 % |
|---|---|---|---|---|---|---|
| 16 °C | 6.1 g/m³ · 4.1 °C | 6.8 g/m³ · 5.6 °C | 7.5 g/m³ · 7.0 °C | 8.2 g/m³ · 8.2 °C | 8.8 g/m³ · 9.4 °C | 9.5 g/m³ · 10.5 °C |
| 18 °C | 6.9 g/m³ · 5.9 °C | 7.7 g/m³ · 7.4 °C | 8.4 g/m³ · 8.8 °C | 9.2 g/m³ · 10.1 °C | 10.0 g/m³ · 11.3 °C | 10.7 g/m³ · 12.4 °C |
| 20 °C | 7.8 g/m³ · 7.7 °C | 8.6 g/m³ · 9.3 °C | 9.5 g/m³ · 10.7 °C | 10.3 g/m³ · 12.0 °C | 11.2 g/m³ · 13.2 °C | 12.1 g/m³ · 14.4 °C |
| 22 °C | 8.7 g/m³ · 9.5 °C | 9.7 g/m³ · 11.1 °C | 10.7 g/m³ · 12.5 °C | 11.6 g/m³ · 13.9 °C | 12.6 g/m³ · 15.1 °C | 13.6 g/m³ · 16.3 °C |
| 24 °C | 9.8 g/m³ · 11.3 °C | 10.9 g/m³ · 12.9 °C | 11.9 g/m³ · 14.4 °C | 13.0 g/m³ · 15.8 °C | 14.1 g/m³ · 17.0 °C | 15.2 g/m³ · 18.2 °C |
<!-- END dew-points -->

## 2. When ventilation dries the room

The blueprint compares the room air with the outdoor air **as it would be after warming up (or cooling down) to room temperature**:

```
drying effect = RH_room − RH_outdoor · e_s(T_outdoor) / e_s(T_room)     (percentage points)
```

This is how far the room humidity can drop by ventilating. Ventilation is recommended when the drying effect reaches the **Minimum Drying Effect** (default 6 points). This is the same as a dew point comparison, only easier to read: at 20 °C room temperature, 6 points correspond to about 1.5 to 2 K dew point difference.

The outdoor RH alone says little. Outdoor air at 20 °C room temperature:

<!-- BEGIN outdoor-air -->
| Outdoor air | 40 % | 60 % | 80 % | 100 % |
|---|---|---|---|---|
| −10 °C | 5 % | 7 % | 10 % | 12 % |
| −5 °C | 7 % | 11 % | 14 % | 18 % |
| 0 °C | 10 % | 16 % | 21 % | 26 % |
| 5 °C | 15 % | 22 % | 30 % | 37 % |
| 10 °C | 21 % | 32 % | 42 % | 53 % |
| 15 °C | 29 % | 44 % | 58 % | 73 % |
| 20 °C | 40 % | 60 % | 80 % | 100 % |
| 25 °C | 54 % | 81 % | condenses | condenses |
| 30 °C | 73 % | condenses | condenses | condenses |
<!-- END outdoor-air -->

Foggy winter air at 0 °C / 100 % ends up at about 26 % in the room and dries it very well. Summer air at 25 °C / 60 % ends up at 81 % and makes the room wetter, although it "only" has 60 % outside.

Why a minimum effect at all: humidity sensors are typically accurate to ±2 % RH and ±0.2 K, and a weather service measures at a station nearby, not in front of your window. Together this adds up to about ±1 K dew point, or ±3 to 4 points, on the difference. Below that, a recommendation could be pure measurement noise. In winter every ventilation also costs heating energy, so small effects are not worth it.

## 3. Decision logic

The automation runs every 5 minutes and whenever the room humidity, a window/door or the presence changes. The first matching rule wins:

| # | Condition | Dehumidifier |
|---|---|---|
| 1 | Time window enabled and outside it, unless "Emergency Also Outside the Time Window" is on and there is an emergency | off |
| 2 | Room humidity ≥ emergency humidity (60 %); with an open window only if "Emergency Also With Open Windows" is on | on |
| 3 | A window or door is open, unless "Emergency Also With Open Windows" is on and there is an emergency | off |
| 4 | Ventilation was recommended for the whole wait time (30 min) and nobody opened a window, or Home Assistant restarted/reloaded | on |
| 5 | Ventilation is recommended and "please ventilate" actions are set | waits (no change) |
| 6 | Room humidity ≥ turn-on humidity (55 %) | on |
| 7 | Room humidity < turn-off humidity (50 %) and minimum run time (15 min) reached | off |
| – | Otherwise (between both thresholds) | no change |

Turning on always respects the minimum off time (5 min), which protects the compressor. If the turn-off humidity is set at or above the turn-on humidity, 2 points below the turn-on humidity are used, so there is always a gap between switching on and off.

**Emergency** means the room humidity is at or above the emergency humidity, or the dehumidifier is running and the humidity is less than 2 points below it. Without these 2 points the dehumidifier would switch on and off every few minutes around the emergency humidity, for example at night or with an open window. With an open window or outside the time window, an emergency run ends as soon as the humidity falls 2 points below the emergency humidity; the minimum run time does not delay this. Both emergency options are off by default: an open window dries the room faster than the dehumidifier, and the time window is usually meant as quiet time.

**Ventilation is recommended** when all of these apply:

- indoor temperature, outdoor temperature and outdoor humidity are available,
- inside the time window (if enabled), someone is home (or no presence sensors are set) and no window is open,
- room humidity ≥ turn-on humidity,
- drying effect ≥ minimum drying effect,
- outdoor temperature ≤ maximum comfort temperature **or** ≤ room temperature, so ventilating cannot heat the room above your comfort level,
- room temperature ≥ minimum room temperature (18 °C), so the walls do not cool down in winter.

The "please ventilate" actions run once when the recommendation starts. After a restart or a reload of the automations the 30-minute timer cannot continue, so the dehumidifier takes over right away if the humidity is at or above the turn-on humidity.

**"Close the window" actions** run once per opening (inside the time window) as soon as one of these applies:

- the window has been open for the maximum time (table in section 4),
- the room fell below the minimum room temperature while it is colder outside,
- the air is exchanged: open for at least 3 minutes and the drying effect is below half the minimum drying effect. This also applies when the outdoor air was not drier in the first place.

**Variables for your actions:** `indoor_humidity` (room humidity in %) and `drying_potential` (drying effect in percentage points, empty without the ventilation sensors). Example:

```yaml
- action: notify.mobile_app_my_phone
  data:
    title: Please ventilate
    message: >
      Room humidity {{ indoor_humidity }} %. Ventilating lowers it by about
      {{ drying_potential }} percentage points.
```

**Device hygrostat:** many dehumidifiers measure humidity in their own, already dried air stream and stop too early. With "Bypass the Device's Own Humidity Control" the automation sets the device's target humidity to its minimum whenever it turns the device on, so only the room sensor decides when it stops.

## 4. Ventilating in practice

Maximum ventilation time before the "close the window" actions run:

| Outdoor temperature | Maximum time |
|---|---|
| below 5 °C | 5 min |
| 5 to 10 °C | 10 min |
| 10 to 15 °C | 15 min |
| 15 to 20 °C | 20 min |
| 20 °C and above | 25 min |
| unknown | 10 min |

This follows the usual advice of the Umweltbundesamt and the Verbraucherzentrale (3–5 minutes in winter, 10–20 minutes in spring and autumn, longer in summer), converted from months to outdoor temperatures.

- **Shock ventilation instead of tilted windows.** A fully open window exchanges the air of a 50 m³ room in a few minutes; a tilted window needs about 40 minutes and cools the walls around it.
- **Winter** is the best season for ventilating: cold air holds little water. One full air exchange of a 50 m³ room at 20 °C / 55 % with outdoor air at 0 °C / 85 % removes about 0.3 litres of water.
- **Summer:** ventilate at night or in the early morning. Warm, humid daytime air cools down on cold basement walls (12–14 °C) and can even condense there. The dew point comparison prevents such recommendations: they only come when the outdoor air is clearly drier than the room air.
- **Rebound:** walls, furniture and textiles store far more water than the room air (50 m³ at 20 °C / 60 % hold only about 0.5 litres). After ventilating they release moisture again and the humidity rises. If the conditions still apply, the blueprint recommends ventilating again.

## 5. Mould and cold walls

- Below about **70 %** RH at a surface, mould does not grow. **70–80 %** over a longer time is enough for many species, from **80 %** growth is likely. The German standard DIN 4108-2 uses 80 % at the surface as its criterion.
- At a cold wall the air cools down and its RH rises. Room air at 20 °C:

<!-- BEGIN surface -->
| Room air 20 °C | wall 18 °C | wall 16 °C | wall 14 °C | wall 12 °C |
|---|---|---|---|---|
| 45 % | 51 % | 58 % | 66 % | **75 %** |
| 50 % | 57 % | 64 % | **73 %** | **83 %** |
| 55 % | 62 % | **71 %** | **80 %** | **92 %** |
| 60 % | 68 % | **77 %** | **88 %** | **100 %** |
| 65 % | **74 %** | **84 %** | **95 %** | **100 %** |
<!-- END surface -->

Values of 70 % and above are shown in bold. Room air at 55 % already reaches 80 % at a 14 °C wall. Basement walls in contact with the ground are often that cold, which is why the defaults (turn-on 55 %, turn-off 50 %, emergency 60 %) are stricter than the general 40–60 % recommendation.

## 6. Dehumidifier efficiency

- **Rated vs. real capacity:** manufacturers state the extraction at 30 °C / 80 %. At 20 °C / 60 % a typical 20-litre unit removes only about 8.5 litres per day. Below about 15 °C compressor dehumidifiers lose much of their efficiency, below about 5 °C the coil ices up.
- **Drying deeper costs more:** the drier the air, the less water each kWh removes. In a US simulation, a 50 % setpoint used about five times the energy of 60 %. Don't set the turn-off humidity lower than necessary.
- **Short cycles cost efficiency** (about 16 % in one measurement), which is why there is a minimum run time (15 min) and a minimum off time (5 min).
- **Heat:** all electrical energy plus the heat released by the condensing water (about 0.7 kWh per litre) warms the room. In winter this partly replaces heating, in summer it is unwanted.
- **Ventilate or dehumidify in winter?** Roughly the same cost. Ventilating wins with a large drying effect and cheap heat, the dehumidifier wins with a small effect. This is another reason for the minimum drying effect.

## 7. Scenarios

All values are calculated with the formulas above and the logic of version 3.0.

- **Indoor / Outdoor:** temperature / relative humidity.
- **Δ dew point:** indoor minus outdoor dew point. Positive means the outdoor air contains less water.
- **Outdoor air in the room:** the RH the outdoor air would have at room temperature.
- **Drying effect:** room RH minus the previous column.
- **Settings:** "defaults" means turn-on 55 %, turn-off 50 %, emergency 60 %, minimum drying effect 6 points, comfort 20 °C, minimum room temperature 18 °C, wait time 30 min, minimum run time 15 min, minimum off time 5 min. Changed values are bold.
- **Situation:** unless stated otherwise, someone is home, all windows are closed, the dehumidifier has been off for a long time, it is 14:00 and "please ventilate" actions are set.

### Winter

<!-- BEGIN scenarios-winter -->
| # | Indoor | Indoor AH / dew point | Outdoor | Outdoor AH / dew point | Δ dew point | Outdoor air in the room | Drying effect | Settings | Situation | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 °C / 58 % | 10.0 g/m³ / 11.5 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +11.0 K | 27 % | +31 pts | defaults | – | **Ventilate**, dehumidifier waits – outdoor air 31 points drier |
| 2 | 20 °C / 58 % | 10.0 g/m³ / 11.5 °C | −5 °C / 80 % | 2.7 g/m³ / −7.9 °C | +19.4 K | 14 % | +44 pts | defaults | – | **Ventilate**, dehumidifier waits – outdoor air 44 points drier |
| 3 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | 5 °C / 95 % | 6.5 g/m³ / 4.3 °C | +7.9 K | 33 % | +24 pts | defaults | fog outside | **Ventilate**, dehumidifier waits – outdoor air 24 points drier |
| 4 | 20 °C / 56 % | 9.7 g/m³ / 11.0 °C | 8 °C / 90 % | 7.4 g/m³ / 6.5 °C | +4.5 K | 41 % | +15 pts | defaults | – | **Ventilate**, dehumidifier waits – outdoor air 15 points drier |
| 5 | 17 °C / 58 % | 8.4 g/m³ / 8.7 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +8.1 K | 33 % | +25 pts | defaults | – | Dehumidifier **on** – room below 18 °C |
| 6 | 17 °C / 58 % | 8.4 g/m³ / 8.7 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +8.1 K | 33 % | +25 pts | **min. room 16 °C** | – | **Ventilate**, dehumidifier waits – outdoor air 25 points drier |
| 7 | 20 °C / 57 % | 9.8 g/m³ / 11.2 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +10.7 K | 27 % | +30 pts | defaults | nobody home | Dehumidifier **on** – nobody home |
| 8 | 20 °C / 62 % | 10.7 g/m³ / 12.5 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +12.0 K | 27 % | +35 pts | defaults | – | Dehumidifier **on** – emergency humidity (≥ 60 %); ventilation is recommended as well |
| 9 | 20 °C / 57 % | 9.8 g/m³ / 11.2 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +10.7 K | 27 % | +30 pts | defaults | window open 4 min | Dehumidifier stays **off** – window open |
| 10 | 20 °C / 57 % | 9.8 g/m³ / 11.2 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +10.7 K | 27 % | +30 pts | defaults | window open 6 min | Dehumidifier stays **off** – window open; **close window** (open ≥ 5 min) |
| 11 | 17.5 °C / 52 % | 7.7 g/m³ / 7.5 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +7.0 K | 32 % | +20 pts | defaults | window open 3 min, room cooled down | Dehumidifier stays **off** – window open; **close window** (room too cold) |
| 12 | 20 °C / 62 % | 10.7 g/m³ / 12.5 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +12.0 K | 27 % | +35 pts | defaults | window open 2 min | Dehumidifier stays **off** – window open |
| 13 | 20 °C / 62 % | 10.7 g/m³ / 12.5 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +12.0 K | 27 % | +35 pts | **emergency with open windows** | window open 2 min | Dehumidifier **on** – emergency humidity (≥ 60 %) |
<!-- END scenarios-winter -->

### Spring and autumn

<!-- BEGIN scenarios-spring -->
| # | Indoor | Indoor AH / dew point | Outdoor | Outdoor AH / dew point | Δ dew point | Outdoor air in the room | Drying effect | Settings | Situation | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| 14 | 21 °C / 58 % | 10.6 g/m³ / 12.4 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +5.7 K | 40 % | +18 pts | defaults | – | **Ventilate**, dehumidifier waits – outdoor air 18 points drier |
| 15 | 21 °C / 58 % | 10.6 g/m³ / 12.4 °C | 15 °C / 85 % | 10.9 g/m³ / 12.5 °C | −0.1 K | 58 % | 0 pts | defaults | – | Dehumidifier **on** – drying effect 0 < 6 points |
| 16 | 19 °C / 56 % | 9.1 g/m³ / 10.0 °C | 14 °C / 70 % | 8.4 g/m³ / 8.6 °C | +1.4 K | 51 % | +5 pts | defaults | – | Dehumidifier **on** – drying effect 5 < 6 points |
| 17 | 19 °C / 56 % | 9.1 g/m³ / 10.0 °C | 14 °C / 70 % | 8.4 g/m³ / 8.6 °C | +1.4 K | 51 % | +5 pts | **min. effect 4 pts** | – | **Ventilate**, dehumidifier waits – outdoor air 5 points drier |
| 18 | 21 °C / 58 % | 10.6 g/m³ / 12.4 °C | 10 °C / 95 % | 8.9 g/m³ / 9.2 °C | +3.2 K | 47 % | +11 pts | defaults | rain | **Ventilate**, dehumidifier waits – outdoor air 11 points drier |
| 19 | 20 °C / 55 % | 9.5 g/m³ / 10.7 °C | 19 °C / 50 % | 8.1 g/m³ / 8.3 °C | +2.3 K | 47 % | +8 pts | defaults | – | **Ventilate**, dehumidifier waits – outdoor air 8 points drier |
| 20 | 20 °C / 55 % | 9.5 g/m³ / 10.7 °C | 19 °C / 50 % | 8.1 g/m³ / 8.3 °C | +2.3 K | 47 % | +8 pts | **min. effect 10 pts** | – | Dehumidifier **on** – drying effect 8 < 10 points |
| 21 | 21 °C / 55 % | 10.1 g/m³ / 11.6 °C | 18 °C / 45 % | 6.9 g/m³ / 5.9 °C | +5.7 K | 37 % | +18 pts | defaults | – | **Ventilate**, dehumidifier waits – outdoor air 18 points drier |
| 22 | 21 °C / 50 % | 9.1 g/m³ / 10.2 °C | 16 °C / 65 % | 8.8 g/m³ / 9.4 °C | +0.8 K | 48 % | +2 pts | defaults | window open 5 min | Dehumidifier stays **off** – window open; **close window** (air exchanged) |
<!-- END scenarios-spring -->

### Summer

<!-- BEGIN scenarios-summer -->
| # | Indoor | Indoor AH / dew point | Outdoor | Outdoor AH / dew point | Δ dew point | Outdoor air in the room | Drying effect | Settings | Situation | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| 23 | 21 °C / 58 % | 10.6 g/m³ / 12.4 °C | 33 °C / 35 % | 12.4 g/m³ / 15.5 °C | −3.1 K | 71 % | −13 pts | defaults | muggy | Dehumidifier **on** – drying effect −13 < 6 points |
| 24 | 21 °C / 58 % | 10.6 g/m³ / 12.4 °C | 33 °C / 25 % | 8.9 g/m³ / 10.4 °C | +2.1 K | 51 % | +7 pts | defaults | dry heat | Dehumidifier **on** – outdoor air warmer than comfort and room |
| 25 | 21 °C / 58 % | 10.6 g/m³ / 12.4 °C | 33 °C / 25 % | 8.9 g/m³ / 10.4 °C | +2.1 K | 51 % | +7 pts | **comfort 30 °C** | dry heat | Dehumidifier **on** – outdoor air warmer than comfort and room |
| 26 | 21 °C / 58 % | 10.6 g/m³ / 12.4 °C | 16 °C / 65 % | 8.8 g/m³ / 9.4 °C | +3.0 K | 48 % | +10 pts | defaults | night | **Ventilate**, dehumidifier waits – outdoor air 10 points drier |
| 27 | 24 °C / 58 % | 12.6 g/m³ / 15.2 °C | 22 °C / 45 % | 8.7 g/m³ / 9.5 °C | +5.7 K | 40 % | +18 pts | defaults | – | **Ventilate**, dehumidifier waits – outdoor air 18 points drier |
| 28 | 24 °C / 58 % | 12.6 g/m³ / 15.2 °C | 26 °C / 40 % | 9.7 g/m³ / 11.4 °C | +3.9 K | 45 % | +13 pts | defaults | – | Dehumidifier **on** – outdoor air warmer than comfort and room |
| 29 | 22 °C / 58 % | 11.2 g/m³ / 13.4 °C | 19 °C / 50 % | 8.1 g/m³ / 8.3 °C | +5.0 K | 42 % | +16 pts | defaults | – | **Ventilate**, dehumidifier waits – outdoor air 16 points drier |
| 30 | 22 °C / 58 % | 11.2 g/m³ / 13.4 °C | 19 °C / 70 % | 11.4 g/m³ / 13.4 °C | 0.0 K | 58 % | 0 pts | defaults | – | Dehumidifier **on** – drying effect 0 < 6 points |
| 31 | 20 °C / 58 % | 10.0 g/m³ / 11.5 °C | 16 °C / 88 % | 12.0 g/m³ / 14.0 °C | −2.5 K | 68 % | −10 pts | defaults | humid morning | Dehumidifier **on** – drying effect −10 < 6 points |
| 32 | 22 °C / 58 % | 11.2 g/m³ / 13.4 °C | 28 °C / 40 % | 10.9 g/m³ / 13.1 °C | +0.2 K | 57 % | +1 pts | defaults | – | Dehumidifier **on** – drying effect 1 < 6 points |
| 33 | 21 °C / 65 % | 11.9 g/m³ / 14.2 °C | 33 °C / 35 % | 12.4 g/m³ / 15.5 °C | −1.3 K | 71 % | −6 pts | defaults | muggy | Dehumidifier **on** – emergency humidity (≥ 60 %) |
<!-- END scenarios-summer -->

### Other settings

<!-- BEGIN scenarios-other -->
| # | Indoor | Indoor AH / dew point | Outdoor | Outdoor AH / dew point | Δ dew point | Outdoor air in the room | Drying effect | Settings | Situation | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| 34 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | 26 °C / 60 % | 14.6 g/m³ / 17.6 °C | −5.5 K | 81 % | −24 pts | **turn-on 60 %, turn-off 55 %, emergency 65 %** | – | No change (stays **off**) – between both thresholds (hysteresis) |
| 35 | 21 °C / 62 % | 11.3 g/m³ / 13.4 °C | 26 °C / 60 % | 14.6 g/m³ / 17.6 °C | −4.2 K | 81 % | −19 pts | **turn-on 60 %, turn-off 55 %, emergency 65 %** | – | Dehumidifier **on** – drying effect −19 < 6 points |
| 36 | 21 °C / 52 % | 9.5 g/m³ / 10.8 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +4.1 K | 40 % | +12 pts | **turn-on 50 %, turn-off 45 %, emergency 58 %** | – | **Ventilate**, dehumidifier waits – outdoor air 12 points drier |
| 37 | 21 °C / 54 % | 9.9 g/m³ / 11.3 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +4.6 K | 40 % | +14 pts | **turn-off 58 %** | turn-off set above turn-on, running | No change (stays **on**) – between both thresholds (hysteresis) |
| 38 | 21 °C / 52 % | 9.5 g/m³ / 10.8 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +4.1 K | 40 % | +12 pts | **turn-off 58 %** | turn-off set above turn-on, running | Dehumidifier **off** – below 53 % |
| 39 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +5.5 K | 40 % | +17 pts | **window 18:00–22:00** | 14:00, outside time window, dehumidifier on | Dehumidifier **off** – outside the time window |
| 40 | 21 °C / 63 % | 11.5 g/m³ / 13.7 °C | 26 °C / 60 % | 14.6 g/m³ / 17.6 °C | −3.9 K | 81 % | −18 pts | **window 18:00–22:00** | 14:00, outside time window | Dehumidifier stays **off** – outside the time window |
| 41 | 21 °C / 63 % | 11.5 g/m³ / 13.7 °C | 26 °C / 60 % | 14.6 g/m³ / 17.6 °C | −3.9 K | 81 % | −18 pts | **window 18:00–22:00, emergency outside window** | 14:00, outside time window | Dehumidifier **on** – emergency humidity (≥ 60 %) |
| 42 | 21 °C / 59 % | 10.8 g/m³ / 12.7 °C | 26 °C / 60 % | 14.6 g/m³ / 17.6 °C | −5.0 K | 81 % | −22 pts | **window 18:00–22:00, emergency outside window** | 14:00, outside time window, emergency run, dehumidifier on | Dehumidifier stays **on** – emergency run continues until below 58 % |
| 43 | 21 °C / 57.5 % | 10.5 g/m³ / 12.3 °C | 26 °C / 60 % | 14.6 g/m³ / 17.6 °C | −5.3 K | 81 % | −24 pts | **window 18:00–22:00, emergency outside window** | 14:00, outside time window, emergency run, dehumidifier on | Dehumidifier **off** – outside the time window |
| 44 | 20 °C / 59 % | 10.2 g/m³ / 11.7 °C | 2 °C / 90 % | 5.0 g/m³ / 0.5 °C | +11.2 K | 27 % | +32 pts | **emergency with open windows** | window open 10 min, emergency run, dehumidifier on | Dehumidifier stays **on** – emergency run continues until below 58 %; **close window** (open ≥ 5 min) |
<!-- END scenarios-other -->

### Special situations

<!-- BEGIN scenarios-special -->
| # | Indoor | Indoor AH / dew point | Outdoor | Outdoor AH / dew point | Δ dew point | Outdoor air in the room | Drying effect | Settings | Situation | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| 45 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | – | – | – | – | – | defaults | no outdoor sensors | Dehumidifier **on** – no ventilation data |
| 46 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | – | – | – | – | – | defaults | no indoor temperature sensor | Dehumidifier **on** – no indoor temperature |
| 47 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +5.5 K | 40 % | +17 pts | defaults | no "please ventilate" actions | Dehumidifier **on** – ventilation not announced (no actions) |
| 48 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +5.5 K | 40 % | +17 pts | defaults | recommended for 30 min, no window opened | Dehumidifier **on** – nobody ventilated within the wait time |
| 49 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +5.5 K | 40 % | +17 pts | defaults | Home Assistant restarted | Dehumidifier **on** – restart: the wait timer starts from scratch |
| 50 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +5.5 K | 40 % | +17 pts | defaults | dehumidifier already running | **Ventilate**, dehumidifier keeps running – outdoor air 17 points drier |
| 51 | 21 °C / 53 % | 9.7 g/m³ / 11.1 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +4.4 K | 40 % | +13 pts | defaults | between thresholds, running | No change (stays **on**) – between both thresholds (hysteresis) |
| 52 | 21 °C / 53 % | 9.7 g/m³ / 11.1 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +4.4 K | 40 % | +13 pts | defaults | between thresholds, off | No change (stays **off**) – between both thresholds (hysteresis) |
| 53 | 21 °C / 49 % | 9.0 g/m³ / 9.9 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +3.2 K | 40 % | +9 pts | defaults | running for 8 min | No change (stays **on**) – minimum run time (8 of 15 min) |
| 54 | 21 °C / 49 % | 9.0 g/m³ / 9.9 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +3.2 K | 40 % | +9 pts | defaults | running for 40 min | Dehumidifier **off** – below 50 % |
| 55 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | 26 °C / 60 % | 14.6 g/m³ / 17.6 °C | −5.5 K | 81 % | −24 pts | defaults | off for 3 min | No change (stays **off**) – compressor protection (3 of 5 min off) |
| 56 | 21 °C / 57 % | 10.4 g/m³ / 12.2 °C | 12 °C / 70 % | 7.4 g/m³ / 6.7 °C | +5.5 K | 40 % | +17 pts | defaults | no presence sensors | **Ventilate**, dehumidifier waits – outdoor air 17 points drier |
<!-- END scenarios-special -->

## 8. Sources

- Umweltbundesamt: [Wie lüfte ich richtig?](https://www.umweltbundesamt.de/themen/gesundheit/umwelteinfluesse-auf-den-menschen/schimmel/wie-luefte-ich-richtig-tipps-tricks-zur) and [Schimmelleitfaden 2017](https://www.nachhaltigesbauen.de/fileadmin/pdf/PDF_weitere_leitfaeden/schimmelpilzleitfaden-umweltbundesamt-2017.pdf)
- Gebäudeforum: [Mindestwärmeschutz, DIN 4108-2](https://www.gebaeudeforum.de/realisieren/bauphysik/mindestwaermeschutz/)
- Verbraucherzentrale: [Heizen und Lüften](https://www.verbraucherzentrale.de/wissen/energie/strom-sparen/heizen-und-lueften-so-gehts-richtig-10426), [Energiesparendes Lüften](https://www.verbraucherzentrale-rlp.de/20-prozent-weniger-heizenergie-nr5-energiesparendes-lueften-82599)
- Verbraucherfenster Hessen: [Kellerlüftung im Sommer](https://verbraucherfenster.hessen.de/freizeit-haushalt/wohnen-garten/kellerlueftung-im-sommer-ist-vorsicht-geboten)
- Make magazine: [Taupunktlüfter](https://github.com/MakeMagazinDE/Taupunktluefter) (dew point controlled ventilation, 5 K + 1 K hysteresis)
- Wetterochs: [Formulas for humidity](https://www.wetterochs.de/wetter/feuchte.html)
- Vaisala: [Relative humidity, dew point, mixing ratio](https://www.vaisala.com/en/application-note/many-faces-of-water-vapor-relative-humidity-dewpoint-mixing-ratio)
- Moisture buffering of building materials: [PMC10141992](https://pmc.ncbi.nlm.nih.gov/articles/PMC10141992/)
- ENERGY STAR: [Dehumidifier testing and capacity](https://www.energystar.gov/products/dehumidifier_testing_and_capacity)
- Meaco: [Dehumidifiers at low temperatures](https://blog.meaco.com/why-desiccant-dehumidifiers-are-not-always-better-at-low-temperature/)
- Energy Vanguard: [Measuring the efficiency of a room dehumidifier](https://www.energyvanguard.com/blog/measuring-the-efficiency-of-a-room-dehumidifier/)
- Building Science Corporation: [Supplemental dehumidification (BA-1310)](https://buildingscience.com/documents/bareports/ba-1310-supplemental-dehumidification-warm-humid-climates/view)
- Home Assistant: [Mold Indicator](https://www.home-assistant.io/integrations/mold_indicator/)
