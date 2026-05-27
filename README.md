# Home Assistant Blueprints

Eine Sammlung von Home Assistant Blueprints für Automationen.

---

## Kategorien

| Ordner | Beschreibung |
|---|---|
| [`climate/`](./climate) | Temperatur, Luftfeuchtigkeit, Heizung, Klimaanlage |
| [`lighting/`](./lighting) | Licht-Automationen und Szenen |
| [`security/`](./security) | Alarmanlagen, Schlösser, Kameras |
| [`presence/`](./presence) | Anwesenheitserkennung, An-/Abwesenheitsroutinen |
| [`energy/`](./energy) | Stromverbrauch, Solar, Lastmanagement |
| [`notifications/`](./notifications) | Benachrichtigungen und Erinnerungen |

---

## Blueprints

### 🌡 Climate

#### Luftentfeuchter Steuerung

Steuert einen Luftentfeuchter dynamisch basierend auf physikalisch fundierter Entscheidungslogik – statt fester Schwellwerte.

**Funktionen:**
- Vergleicht absolute Außen- und Innenluftfeuchtigkeit: Wenn Lüften effizienter wäre, bleibt der Entfeuchter aus
- Berücksichtigt die Außentemperatur: Kein Lüften wenn die Wohnung dadurch über die eingestellte Wohlfühltemperatur aufgeheizt würde
- Optionale Mindest-AH-Differenz: Entfeuchter läuft nur wenn Innenluft deutlich feuchter als Außenluft ist
- Optionale Fenster-/Türsensoren: Entfeuchter schaltet ab wenn ein Fenster geöffnet wird
- Optionale Anwesenheitserkennung: Bei Abwesenheit wird Lüften ignoriert und der Entfeuchter übernimmt
- Kompressorschutz durch konfigurierbare Mindest-Ausschaltzeit
- Notfall-Override bei kritisch hoher Luftfeuchtigkeit (Schimmelschutz)
- Hysterese verhindert Taktung
- Optionales Zeitfenster

**Voraussetzungen:**
- Home Assistant 2024.6 oder neuer
- Sensor für relative Innenluftfeuchtigkeit (Pflicht)
- Sensor für absolute Innenluftfeuchtigkeit (Pflicht)
- Sensoren für Außenluft optional (absolute Feuchte + Temperatur)

[![Blueprint importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Spegeli/homeassistant-blueprints/main/climate/Luftentfeuchter_Steuerung.yaml)

---

## Installation

1. Auf den **„Blueprint importieren"**-Button beim gewünschten Blueprint klicken
2. Im Home Assistant Dialog bestätigen
3. Automation auf Basis des Blueprints erstellen und Sensoren/Geräte zuweisen
