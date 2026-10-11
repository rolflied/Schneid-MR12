# Changelog

Alle nennenswerten Änderungen an der Integration. Format angelehnt an
[Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach
[Semantic Versioning](https://semver.org/lang/de/).

## [0.3.1] – unveröffentlicht

### Behoben
- **Puffer-Ein-/Ausschalttemperatur sind nicht mehr als Eingabefeld
  einstellbar.** 40704/40705 liegen im Block der Ist-/Anzeigewerte und sind
  laut Registerdoku nicht beschreibbar. Das CM-12 quittiert den Schreibbefehl,
  der Regler setzt den Wert aber wieder zurück (an der Anlage bestätigt: 46,0 °C
  geschrieben, nach 195 s wieder 48,0 °C). Die Werte bleiben als Sensoren
  sichtbar; die alten Number-Entitäten werden beim Start automatisch entfernt.

## [0.3.0] – 2026-10-11

Schwerpunkt: Schreibzugriffe über das CM-12 zuverlässig und nachvollziehbar
machen, Entitäten anhand eines vollständigen Registerabzugs der Anlage
(CM-12, Firmware 1.4.2) ausbauen.

### Behoben
- **Geschriebene Werte sprangen nach ca. 30 s zurück.** Die Integration hat
  nach einem Schreibvorgang den neuen Wert sofort in ihren Cache übernommen und
  angezeigt, egal ob das Gerät ihn angenommen hatte. Der nächste Poll zeigte
  dann wieder den echten Wert. Jetzt wird nach dem Schreiben neu gelesen, die
  Anzeige entspricht immer dem Gerät.
- Puffer-Ein-/Ausschalttemperatur (40704/40705) wurden um Faktor 10 zu klein
  geschrieben (45 °C kam als 4,5 °C an). Das Register führt 0,1 °C.
- Schreibfehler wurden nur still geloggt; sie erscheinen jetzt als Fehlermeldung
  in der Oberfläche.
- Temperaturen von genau 12,6 °C wurden als „nicht verfügbar“ verworfen
  (Rohwert 126 galt pauschal als Platzhalter).
- Nachtabsenkungs-Schwellen (40023/40024) werden vorzeichenbehaftet gelesen.
- Datumsregister in `const.py` korrigiert: 717 Wochentag, 718 Tag, 719 Monat,
  720 Jahr (am Gerät bestätigt).
- Heizkurven-Entitäten für Heizkreis 1 werden nur noch angelegt, wenn HK1
  aktiviert ist.
- `pymodbus` fehlte als Abhängigkeit im Manifest.
- Herstellername im Geräteregister: „Schneid“ statt Platzhalter.
- Offset Außentemperatur und Stationserhöhung sind Temperaturdifferenzen und
  werden bei °F-Einstellung nicht mehr falsch umgerechnet.

### Hinzugefügt
- Auswahlfeld **Betriebsmodus je Heizkreis** (40240+n). Der Wert wurde bisher
  gelesen, aber nicht angezeigt.
- Auswahlfelder **Ausheizprogramm** (40030) und **Handbetrieb Primärventil**
  (40050), standardmäßig deaktiviert.
- Einstellbare Systemparameter (Kategorie „Konfiguration“): Offset
  Außentemperatur, Vorlauf bei Frost, Frostschutz-Außentemperatur,
  Stationserhöhung, volle/keine Nachtabsenkung.
- Diagnosesensor **Regler-Uhrzeit**.
- **Prüfung von Schreibvorgängen:** Jeder Schreibvorgang wird beim ersten Poll
  frühestens 60 s später gegen den Gerätewert geprüft und das Ergebnis geloggt
  (`INFO` übernommen / `WARNING` nicht übernommen). Eine sofortige Rücklesung
  zeigt beim CM-12 nur dessen Spiegelregister und sagt nichts darüber, ob der
  Regler den Wert hält.
- `hacs.json` für die Installation über HACS.

### Geändert
- Schreiben erst per FC16 (write multiple registers), bei Ablehnung, Timeout
  oder Verbindungsfehler per FC06 (write single register).
- Lesen und Schreiben laufen über eine gemeinsame Sperre und kommen sich auf der
  Verbindung nicht mehr in die Quere.
- Wärmemenge, Leistung und Volumen des internen Wärmezählers sind bei
  Neuinstallation standardmäßig deaktiviert (liefern ohne Zähler dauerhaft 0).
  Bestehende Installationen behalten ihren Zustand.
- Mindestversion Home Assistant 2024.12 (vorher fälschlich 2024.1 angegeben).
- README: Modbus-TCP-Port 502, CM-12, schreibbare Parameter, Hinweise zur
  Schreibprüfung.

### Hinweis zum Update
- In den Integrationsoptionen nur die tatsächlich vorhandenen Heizkreise
  auswählen. Nicht angeschlossene Kreise zeigen sonst „nicht verfügbar“.
- Ob das CM-12 direkte Modbus-Schreibvorgänge an den Regler weitergibt, ist
  noch nicht bestätigt. Das Log zeigt es nach dem ersten Schreibvorgang.

## [0.2.0] – 2026-03-30

### Hinzugefügt
- Englische Übersetzung des Einrichtungsdialogs.

## [0.1.0] – 2026-03-18

### Hinzugefügt
- Erste Version: Modbus-TCP-Anbindung des Schneid MR-12 mit Sensoren,
  Binärsensoren, schreibbaren Sollwerten und Betriebsmodus, Unterteilung in
  Geräte (Station, Fernwärme, Pufferspeicher, Heizkreise), Nur-Lese-Modus.

[0.3.1]: https://github.com/rolflied/Schneid-MR12/compare/v0.3.0...master
[0.3.0]: https://github.com/rolflied/Schneid-MR12/compare/7c92a3c...ccr-32dc38b4-9q7lxn
[0.2.0]: https://github.com/rolflied/Schneid-MR12/compare/6880ec6...7c92a3c
[0.1.0]: https://github.com/rolflied/Schneid-MR12/commit/6880ec6
