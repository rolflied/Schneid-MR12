# Schneid MR-12 – Home Assistant Integration

![Schneid MR-12](custom_components/schneid_mr12/brand/logo@2x.png)

Custom Integration für die **Schneid MR-12 Fernwärme-Übergabestation** via Modbus TCP.

Die Integration liest Temperaturen, Betriebszustände, Pumpen und den internen Wärmezähler des MR-12 und stellt sie als Home Assistant Entitäten bereit. Schreibbare Parameter (Sollwerte, Betriebsmodi) können optional aktiviert werden.

> **Hinweis:** Diese Integration befindet sich in einem frühen Entwicklungsstadium und wurde an die Bedürfnisse meiner eigenen Anlage angepasst. Es ist möglich, dass andere MR-12-Anlagen abweichende Modbus-Register nutzen oder dass Parameter fehlen, die je nach Anlagenkonfiguration relevant wären. Ich freue mich über Feedback, Fehlermeldungen und Verbesserungsvorschläge – gerne als [Issue](../../issues) oder [Pull Request](../../pulls).

---

## Voraussetzungen

- Home Assistant 2024.1 oder neuer
- Schneid MR-12 mit aktivierter Modbus-TCP-Schnittstelle
- Netzwerkzugang von Home Assistant zur Übergabestation (Standard-Port: 2001)
- `pymodbus` ≥ 3.5.0, < 4.0.0 (wird von HA automatisch verwaltet)

---

## Installation

### Manuell

1. Den Ordner `custom_components/schneid_mr12/` in das Verzeichnis `config/custom_components/` deiner Home Assistant Installation kopieren.
2. Home Assistant neu starten.

### HACS (nicht offiziell gelistet)

1. HACS → Integrationen → ⋮ → Benutzerdefinierte Repositories
2. URL dieses Repositories eintragen, Kategorie: **Integration**
3. Integration installieren und Home Assistant neu starten.

---

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Nach „Schneid MR-12" suchen und auswählen.
3. Verbindungsdaten eingeben:

| Feld | Beschreibung | Standard |
|------|-------------|---------|
| Host | IP-Adresse der Übergabestation | – |
| Port | Modbus-TCP-Port | `2001` |
| Slave-ID | Modbus Slave ID | `1` |
| Abfrageintervall | Sekunden zwischen Aktualisierungen | `30` |
| Heizkreise | Aktive Heizkreise (HK0–HK3) | HK1 |
| Nur-Lesen | Schreibzugriff deaktivieren | nein |

Die Verbindung wird beim Speichern automatisch geprüft.

---

## Entitäten

Die Integration erstellt mehrere Unter-Geräte:

### Hauptgerät
| Entität | Beschreibung |
|---------|-------------|
| Außentemperatur | Aktuelle Außentemperatur |
| Außentemperatur Mittel | Kurzzeit-Mittelwert |
| Außentemperatur Mittel Langzeit | Langzeit-Mittelwert |
| Softwareversion | Diagnose |

### Fernwärme
| Entität | Beschreibung |
|---------|-------------|
| Vorlauf Ist | Sekundärer Vorlauf |
| Vorlauf Soll | Berechneter Sollwert |
| Rücklauf Ist | Sekundärer Rücklauf |
| Rücklauf Primär | Primärseitiger Rücklauf |
| Ventilstellung | Öffnungsgrad des Regelventils (%) |
| Status | Betriebszustand der Übergabe |
| Wärmemenge | Gesamte Wärmeenergie (kWh) |
| Leistung | Aktuelle Wärmeleistung (W) |
| Volumen | Durchgeflossenes Volumen (l) |

### Heizkreis (pro aktiviertem Kreis)
| Entität | Beschreibung |
|---------|-------------|
| Vorlauf Ist / Soll | Heizkreis-Vorlauftemperatur |
| Status | Betriebszustand des Heizkreises |
| Mischer Stellung | Position des Mischers |
| Betriebsmodus | Einstellbar: Auto / Tagbetrieb / Nachtbetrieb / Standby |
| Heizkurven-Sollwerte | Einstellbar: VL-Temperaturen bei +20/+5/−10 °C AT, Min/Max |

### Pufferspeicher
| Entität | Beschreibung |
|---------|-------------|
| Temperatur Oben / Unten | Speicherfühler |
| Pufferpumpe Drehzahl | Aktuelle Pumpendrehzahl (%) |
| Ein-/Ausschalttemperatur | Einstellbar |

### Binärsensoren
Pumpen (Heizkreis, Puffer, Solar) und Fehlermeldungen als `binary_sensor`.

---

## Energie-Dashboard

Der Sensor **Wärmemenge** (`sensor.schneid_mr12_waermemenge`) kann im Home Assistant Energie-Dashboard unter **Gasverbrauch** eingetragen werden. Der Sensor verwendet `device_class: gas` mit der Einheit `kWh` und ist damit direkt kompatibel.

---

## Nur-Lesen-Modus

Wenn **Nur-Lesen** aktiviert ist, werden alle `number`- und `select`-Entitäten deaktiviert. Messwerte bleiben weiterhin verfügbar. Diese Option ist empfehlenswert, wenn der MR-12 primär vom Heizungsfachbetrieb gesteuert wird.

---

## Unterstützte Geräte

Getestet mit:
- **Schneid MR-12** Fernwärme-Übergabestation

---

## Lizenz

MIT License
