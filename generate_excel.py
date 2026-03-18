# -*- coding: utf-8 -*-
"""Schneid MR-12 – Modbus Register Excel-Export."""

import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

with open('C:/Users/rolfl/claudecode/Schneid/modbus_scan.json') as f:
    scan = json.load(f)

SENTINEL = {32766, 65534, 126}


def raw_val(addr_offset):
    """addr_offset = pymodbus-Adresse (PDF - 40000)."""
    v = scan.get(str(addr_offset))
    return int(v) if v is not None else None


def r32(pdf_reg):
    hi = raw_val(pdf_reg - 40000)
    lo = raw_val(pdf_reg - 40000 + 1)
    if hi is None or lo is None:
        return None
    return (hi << 16) | lo


# ─── Register-Datenbank ──────────────────────────────────────────────────────
registers = []


def add(reg, desc, kat, einh='', skal='raw', rw='R'):
    registers.append({
        'reg': reg, 'desc': desc, 'kat': kat,
        'einheit': einh, 'skalierung': skal, 'rw': rw
    })


# Konfiguration 40000-40011
for r, nm in [
    (40000, 'Konfiguration Basis C'), (40001, 'Konfiguration Basis B'),
    (40002, 'Konfiguration Modul 1'), (40003, 'Konfiguration Modul 2'),
    (40004, 'Konfiguration Modul 3'), (40005, 'Konfiguration Modul 4'),
    (40006, 'Konfiguration Modul 5'), (40007, 'Konfiguration Modul 6'),
    (40008, 'Konfiguration Modul 7'), (40009, 'Konfiguration Basis D'),
    (40010, 'Konfiguration Basis A'), (40011, 'Boiler primaer-seitig'),
]:
    add(r, nm, 'Konfiguration', '', 'raw', 'R/W')

# Systemparameter 40012-40099
add(40012, 'Offset Aussentemperatur', 'System', 'C', 'x0.1', 'R/W')
add(40013, 'Betriebsart Solaranlage', 'System', '', 'raw', 'R/W')
add(40014, 'Max. Puffertemperatur', 'System', 'C', 'x1', 'R/W')
add(40015, 'Max. Kollektortemperatur', 'System', 'C', 'x1', 'R/W')
add(40016, 'Einschalthysterese', 'System', 'C', 'x1', 'R/W')
add(40017, 'Handbetrieb Solarpumpe', 'System', '%', 'x1', 'R/W')
add(40018, 'Min. Drehzahl Solar', 'System', '%', 'x1', 'R/W')
add(40019, 'Handbetrieb Aout', 'System', '%', 'x1', 'R/W')
add(40020, 'Dauer Partymodus', 'System', 'h', 'x1', 'R/W')
add(40021, 'Abschaltung Pumpen', 'System', '', 'raw', 'R/W')
add(40022, 'Ein/Aus Anhebung', 'System', '%', 'x1', 'R/W')
add(40023, 'Volle Nachtabsenkung', 'System', 'C', 'x1', 'R/W')
add(40024, 'Keine Nachtabsenkung', 'System', 'C', 'x1', 'R/W')
add(40025, 'Hysterese Thermostatregler', 'System', 'C', 'x0.1', 'R/W')
add(40026, 'Einschalttemperatur Zirkulationspumpe', 'System', 'C', 'x1', 'R/W')
add(40027, 'AT Mittel Regelung x15m', 'System', '', 'raw', 'R/W')
add(40028, 'Vorlauftemperatur bei Frost', 'System', 'C', 'x1', 'R/W')
add(40029, 'Frostschutztemperatur Aussen', 'System', 'C', 'x1', 'R/W')
add(40030, 'Ausheizprogramm Ja/Nein', 'System', '', 'raw', 'R/W')
add(40031, 'Start Temperatur Ausheizung', 'System', 'C', 'x1', 'R/W')
add(40032, 'Stop Temperatur Ausheizung', 'System', 'C', 'x1', 'R/W')
for i in range(40033, 40049):
    add(i, f'Systemparameter {i}', 'System', '', 'raw', 'R/W')
add(40049, 'Stationserhöhung', 'Ferwaerme', 'C', 'x1', 'R/W')
add(40050, 'Handbetrieb Ventil', 'Ferwaerme', '%', 'x1', 'R/W')
add(40051, 'Systemparameter 40051', 'System', '', 'raw', 'R/W')
add(40052, 'Systemparameter 40052', 'System', '', 'raw', 'R/W')
add(40053, 'Leistungsbegrenzung', 'Ferwaerme', '', 'raw', 'R/W')
for i in range(40054, 40066):
    add(i, f'Systemparameter {i}', 'System', '', 'raw', 'R/W')
add(40066, 'Einstellbare Zeitraeume', 'System', '', 'raw', 'R/W')
add(40067, 'Sprache', 'System', '', 'raw', 'R/W')
add(40068, 'Helligkeit Backlight', 'System', '', 'raw', 'R/W')
add(40069, 'Kontrast Display', 'System', '', 'raw', 'R/W')
add(40070, 'Heizkreisbezeichnung', 'System', '', 'raw', 'R/W')
add(40071, 'Daten in SinVis', 'System', '', 'raw', 'R/W')
add(40072, 'Waermezaehlertyp', 'System', '', 'raw', 'R/W')
add(40073, 'Anzahl MBus Geraete', 'System', '', 'raw', 'R/W')
add(40074, 'Adresse ComA', 'System', '', 'raw', 'R/W')
add(40075, 'Adresse ComC', 'System', '', 'raw', 'R/W')
add(40076, 'Baudrate ComA', 'System', '', 'raw', 'R/W')
add(40077, 'Baudrate ComB', 'System', '', 'raw', 'R/W')
add(40078, 'Baudrate ComC', 'System', '', 'raw', 'R/W')
add(40079, 'Kaltstart', 'System', '', 'raw', 'R/W')
add(40080, 'Boilersolltemp. 1', 'Boiler', 'C', 'x1', 'R/W')
add(40081, 'Boilerminimaltemp. 1', 'Boiler', 'C', 'x1', 'R/W')
add(40082, 'Boilerausschalttemp. 1', 'Boiler', 'C', 'x1', 'R/W')
add(40083, 'Boilerladetemp. Soll 1', 'Boiler', 'C', 'x1', 'R/W')
add(40084, 'Boilerladetemp. Min 1', 'Boiler', 'C', 'x1', 'R/W')
add(40085, 'Legionellenladung 1', 'Boiler', '', 'raw', 'R/W')
add(40086, 'Hysterese Boiler Ladezeit 1', 'Boiler', 'C', 'x1', 'R/W')
add(40087, 'Nachlaufzeit Boilerpumpe 1', 'Boiler', 'min', 'x1', 'R/W')
add(40088, 'Boilerladeart 1', 'Boiler', '', 'raw', 'R/W')
add(40089, 'Boilersperre 1', 'Boiler', '', 'raw', 'R/W')
add(40090, 'Boilersolltemp. 2', 'Boiler', 'C', 'x1', 'R/W')
add(40091, 'Boilerminimaltemp. 2', 'Boiler', 'C', 'x1', 'R/W')
add(40092, 'Boilerausschalttemp. 2', 'Boiler', 'C', 'x1', 'R/W')
add(40093, 'Boilerladetemp. Soll 2', 'Boiler', 'C', 'x1', 'R/W')
add(40094, 'Boilerladetemp. Min 2', 'Boiler', 'C', 'x1', 'R/W')
add(40095, 'Legionellenladung 2', 'Boiler', '', 'raw', 'R/W')
add(40096, 'Hysterese Boiler Ladezeit 2', 'Boiler', 'C', 'x1', 'R/W')
add(40097, 'Nachlaufzeit Boilerpumpe 2', 'Boiler', 'min', 'x1', 'R/W')
add(40098, 'Boilerladeart 2', 'Boiler', '', 'raw', 'R/W')
add(40099, 'Boilersperre 2', 'Boiler', '', 'raw', 'R/W')

# HK0-7 Parameter 40100-40211
hk_param_names = [
    ('Abschalttemperatur Tagbetrieb', 'C', 'x1'),
    ('Abschalttemperatur Absenkung', 'C', 'x1'),
    ('Raumsolltemperatur', 'C', 'x0.1'),
    ('VL Soll bei +20AT', 'C', 'x1'),
    ('VL Soll bei +5AT', 'C', 'x1'),
    ('VL Soll bei -10AT', 'C', 'x1'),
    ('Max. Vorlauftemperatur', 'C', 'x1'),
    ('Min. Vorlauftemperatur', 'C', 'x1'),
    ('Warmwassernachrang', '', 'raw'),
    ('Timer Heizkreis', 's', 'x1'),
    ('Faktor Heizkreis', '', 'raw'),
    ('Raumeinfluss Heizkreis', '%', 'x1'),
    ('Faktor Raumregelung', '', 'raw'),
    ('Offset Raumtemperatur', 'C', 'x0.1'),
]
for hk in range(8):
    base = 40100 + hk * 14
    for off, (nm, einh, skal) in enumerate(hk_param_names):
        add(base + off, f'HK{hk} {nm}', f'Heizkreis{hk}', einh, skal, 'R/W')

add(40212, '(reserviert)', 'System', '', 'raw', 'R/W')
add(40213, 'Tagpoti WUEST', 'WUEST', 'C', 'x0.1', 'R/W')
add(40214, 'Nachtpoti WUEST', 'WUEST', 'C', 'x0.1', 'R/W')

# WÜST + Betriebsmodi 40215-40244
add(40215, 'Funktion WUEST', 'WUEST', '', 'raw', 'R/W')
add(40216, 'Urlaubszeitraum VON Tag', 'WUEST', '', 'raw', 'R/W')
add(40217, 'Urlaubszeitraum VON Monat', 'WUEST', '', 'raw', 'R/W')
add(40218, 'Urlaubszeitraum VON Jahr', 'WUEST', '', 'raw', 'R/W')
add(40219, 'Urlaubszeitraum BIS Tag', 'WUEST', '', 'raw', 'R/W')
add(40220, 'Urlaubszeitraum BIS Monat', 'WUEST', '', 'raw', 'R/W')
add(40221, 'Urlaubszeitraum BIS Jahr', 'WUEST', '', 'raw', 'R/W')
add(40222, 'Boilerladezeitraum 1 Boiler1 Von', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40223, 'Boilerladezeitraum 1 Boiler1 Bis', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40224, 'Boilerladezeitraum 2 Boiler1 Von', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40225, 'Boilerladezeitraum 2 Boiler1 Bis', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40226, 'Boilerladezeitraum 3 Boiler1 Von', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40227, 'Boilerladezeitraum 3 Boiler1 Bis', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40228, 'Boilerladezeitraum 1 Boiler2 Von', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40229, 'Boilerladezeitraum 1 Boiler2 Bis', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40230, 'Boilerladezeitraum 2 Boiler2 Von', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40231, 'Boilerladezeitraum 2 Boiler2 Bis', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40232, 'Boilerladezeitraum 3 Boiler2 Von', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40233, 'Boilerladezeitraum 3 Boiler2 Bis', 'Boiler', 'hhmm', 'raw', 'R/W')
for i in range(40234, 40240):
    add(i, f'(reserviert {i})', 'System', '', 'raw', 'R/W')
add(40240, 'Betriebsmodus HK0', 'Heizkreis0', '', 'raw', 'R/W')
add(40241, 'Betriebsmodus HK1', 'Heizkreis1', '', 'raw', 'R/W')
add(40242, 'Betriebsmodus HK2', 'Heizkreis2', '', 'raw', 'R/W')
add(40243, 'Betriebsmodus HK3', 'Heizkreis3', '', 'raw', 'R/W')
add(40244, 'Betriebsmodus HK4', 'Heizkreis4', '', 'raw', 'R/W')

# Zeitprogramme 40245-40599
for i in range(40245, 40600):
    add(i, 'Heiz-/Absenkzeit Zeitprogramm', 'Zeitprogramm', 'hhmm', 'raw', 'R/W')

# Ist-Werte 40600-40609
add(40600, 'T6 Aussentemperatur', 'Ferwaerme', 'C', 'x0.1', 'R')
add(40601, 'T7 RL Primaer Ist', 'Ferwaerme', 'C', 'x0.1', 'R')
add(40602, 'T8 VL Sekundaer Ist', 'Ferwaerme', 'C', 'x0.1', 'R')
add(40603, 'T11 RL Sekundaer Ist', 'Ferwaerme', 'C', 'x0.1', 'R')
add(40604, 'Solltemperatur VL Sekundaer', 'Ferwaerme', 'C', 'x0.1', 'R')
add(40605, 'Max. Ruecklauftemperatur Primaer', 'Ferwaerme', 'C', 'x0.1', 'R')
add(40606, 'Status Uebergabestation', 'Ferwaerme', '', 'raw', 'R')
add(40607, '(reserviert)', 'System', '', 'raw', 'R')
add(40608, '(reserviert)', 'System', '', 'raw', 'R')
add(40609, '(reserviert/Ventilstellung FW?)', 'Ferwaerme', '', 'raw', 'R')

# HK0-7 Ist-Werte 40610-40689
for hk in range(8):
    base = 40610 + hk * 10
    add(base + 0, f'VL Heizkreis {hk} Ist', f'Heizkreis{hk}', 'C', 'x0.1', 'R')
    add(base + 1, f'Solltemperatur Heizkreis {hk}', f'Heizkreis{hk}', 'C', 'x0.1', 'R')
    add(base + 2, f'Raumsolltemperatur Heizkreis {hk}', f'Heizkreis{hk}', 'C', 'x0.1', 'R')
    add(base + 3, f'Raumtemperatur Heizkreis {hk}', f'Heizkreis{hk}', 'C', 'x0.1', 'R')
    add(base + 4, f'Potentiometer Fernbedienung {hk}', f'Heizkreis{hk}', '', 'x0.1', 'R')
    add(base + 5, f'Fernbedienung {hk}', f'Heizkreis{hk}', '', 'raw', 'R')
    add(base + 6, f'Pumpe Heizkreis {hk}', f'Heizkreis{hk}', '', 'raw', 'R')
    add(base + 7, f'Status Heizkreis {hk}', f'Heizkreis{hk}', '', 'raw', 'R')
    add(base + 8, f'Status Mischer Heizkreis {hk}', f'Heizkreis{hk}', '', 'raw', 'R')
    add(base + 9, f'(reserviert HK{hk})', f'Heizkreis{hk}', '', 'raw', 'R')

# Boiler + Diagnose 40690-40729
add(40690, 'T9 Speicher 1 oben', 'Puffer', 'C', 'x0.1', 'R')
add(40691, 'T10 Speicher 1 unten', 'Puffer', 'C', 'x0.1', 'R')
add(40692, 'Solltemperatur VL Boiler 1', 'Boiler', 'C', 'x0.1', 'R')
add(40693, 'Status Boilerkreis 1', 'Boiler', '', 'raw', 'R')
add(40694, 'Pumpe Boiler 1', 'Boiler', '', 'raw', 'R')
add(40695, 'T12 Speicher 2 oben', 'Boiler', 'C', 'x0.1', 'R')
add(40696, 'T13 Speicher 2 unten', 'Boiler', 'C', 'x0.1', 'R')
add(40697, 'Solltemperatur VL Boiler 2', 'Boiler', 'C', 'x0.1', 'R')
add(40698, 'Status Boilerkreis 2', 'Boiler', '', 'raw', 'R')
add(40699, 'Pumpe Boiler 2', 'Boiler', '', 'raw', 'R')
add(40700, 'Temp. VL Lademodul 1', 'Lademodul', 'C', 'x0.1', 'R')
add(40701, 'Temp. VL Lademodul 2', 'Lademodul', 'C', 'x0.1', 'R')
add(40702, 'Temp. Zirkulation 1', 'Zirkulation', 'C', 'x0.1', 'R')
add(40703, 'Temp. Zirkulation 2', 'Zirkulation', 'C', 'x0.1', 'R')
add(40704, 'Einschalttemperatur Puffer', 'Puffer', 'C', 'x0.1', 'R')
add(40705, 'Ausschalttemperatur Puffer', 'Puffer', 'C', 'x0.1', 'R')
add(40706, 'Drehzahl Puffer', 'Puffer', '%', 'raw', 'R')
add(40707, 'Drehzahl Solar', 'Solar', '%', 'raw', 'R')
add(40708, 'Zubringpumpe', 'Ferwaerme', '', 'raw', 'R')
add(40709, 'Ventilstellung', 'Ferwaerme', '%', 'raw', 'R')
add(40710, 'Status SD-Card', 'Diagnose', '', 'raw', 'R')
add(40711, 'Version Software', 'Diagnose', '', 'raw', 'R')
add(40712, 'Hydraulikvariante', 'Diagnose', '', 'raw', 'R')
add(40713, 'Technikebene Menu', 'Diagnose', '', 'raw', 'R')
add(40714, 'Zirkulationspumpe 1', 'Zirkulation', '', 'raw', 'R')
add(40715, 'Zirkulationspumpe 2', 'Zirkulation', '', 'raw', 'R')
add(40716, 'Uhrzeit Regler', 'System', 'hhmm', 'raw', 'R')
add(40717, 'Tag Regler', 'System', '', 'raw', 'R')
add(40718, 'Monat Regler', 'System', '', 'raw', 'R')
add(40719, 'Wochentag Regler', 'System', '', 'raw', 'R')
add(40720, 'Jahr Regler', 'System', '', 'raw', 'R')
add(40721, 'Status Pumpe Lademodul 1', 'Lademodul', '', 'raw', 'R')
add(40722, 'Status Mischer Lademodul 1', 'Lademodul', '', 'raw', 'R')
add(40723, 'Status Pumpe Lademodul 2', 'Lademodul', '', 'raw', 'R')
add(40724, 'Status Mischer Lademodul 2', 'Lademodul', '', 'raw', 'R')
add(40725, 'HK-Module', 'System', '', 'raw', 'R')
add(40726, 'Reset Counter', 'Diagnose', '', 'raw', 'R')
add(40727, '(reserviert)', 'System', '', 'raw', 'R')
add(40728, 'Aussentemperatur Mittel', 'Ferwaerme', 'C', 'x0.1', 'R')
add(40729, 'Aussentemperatur Mittel Langzeit', 'Ferwaerme', 'C', 'x0.1', 'R')

# Interner Waermezaehler 40730-40739
add(40730, 'Waermemenge HIGH (intern)', 'Waermezaehler', '', 'raw', 'R')
add(40731, 'Waermemenge LOW (intern) -> 32bit /10 = kWh', 'Waermezaehler', '0.1kWh', 'raw', 'R')
add(40732, 'Volumen HIGH (intern)', 'Waermezaehler', '', 'raw', 'R')
add(40733, 'Volumen LOW (intern) -> 32bit = Liter', 'Waermezaehler', 'l', 'raw', 'R')
add(40734, 'Leistung HIGH (intern)', 'Waermezaehler', '', 'raw', 'R')
add(40735, 'Leistung LOW (intern) -> 32bit = Watt', 'Waermezaehler', 'W', 'raw', 'R')
add(40736, 'Stichtagszaehlerstand HIGH', 'Waermezaehler', '', 'raw', 'R')
add(40737, 'Stichtagszaehlerstand LOW', 'Waermezaehler', '', 'raw', 'R')
add(40738, 'Seriennummer HIGH', 'Waermezaehler', '', 'raw', 'R')
add(40739, 'Seriennummer LOW', 'Waermezaehler', '', 'raw', 'R')

# Diagnose 40740-40799
for i in range(40740, 40768):
    add(i, f'(MBus/reserviert {i})', 'Diagnose', '', 'raw', 'R')
add(40767, 'Version (MBus)', 'Diagnose', '', 'raw', 'R')
add(40768, 'AHZWertVon', 'Diagnose', '', 'raw', 'R')
add(40769, 'AHZWertBis', 'Diagnose', '', 'raw', 'R')
add(40770, 'AHZWertAkt', 'Diagnose', '', 'raw', 'R')
add(40771, 'AHZWertSumme', 'Diagnose', '', 'raw', 'R')
add(40772, 'Relais 1..8', 'Diagnose', '', 'raw', 'R')
add(40773, 'Relais 9..16', 'Diagnose', '', 'raw', 'R')
add(40774, 'Relais 17..24', 'Diagnose', '', 'raw', 'R')
add(40775, 'Relais 25..32', 'Diagnose', '', 'raw', 'R')
add(40776, 'ZDin bitcodiert', 'Diagnose', '', 'raw', 'R')
add(40777, 'ZDin_inv bitcodiert', 'Diagnose', '', 'raw', 'R')
for i in range(40778, 40785):
    add(i, f'(reserviert {i})', 'Diagnose', '', 'raw', 'R')
add(40785, 'Aout 1', 'Diagnose', '%', 'raw', 'R')
add(40786, 'Aout 2', 'Diagnose', '%', 'raw', 'R')
add(40787, 'Aout 3', 'Diagnose', '%', 'raw', 'R')
add(40788, 'Aout 4', 'Diagnose', '%', 'raw', 'R')
add(40789, 'ZAin 1', 'Diagnose', 'x.x%', 'x0.1', 'R')
add(40790, 'ZAin 2', 'Diagnose', 'x.x%', 'x0.1', 'R')
add(40791, 'ZAin 3', 'Diagnose', 'x.x%', 'x0.1', 'R')
add(40792, 'ZAin 4', 'Diagnose', 'x.x%', 'x0.1', 'R')
add(40793, 'ZAin 5', 'Diagnose', 'x.x%', 'x0.1', 'R')
add(40794, 'ZAin 6', 'Diagnose', 'x.x%', 'x0.1', 'R')
add(40795, 'ZAin 7', 'Diagnose', 'x.x%', 'x0.1', 'R')
add(40796, 'ZAin 8', 'Diagnose', 'x.x%', 'x0.1', 'R')
add(40797, 'Firmware Build Number', 'Diagnose', '', 'raw', 'R')
add(40798, 'SPS-Version (0=Nein 1=Ja)', 'Diagnose', '', 'raw', 'R')
add(40799, '(reserviert)', 'System', '', 'raw', 'R')

# Offsets + erweiterte Konfiguration 40800-40999
for i in range(40800, 40814):
    add(i, f'(reserviert/Diagnose {i})', 'System', '', 'raw', 'R')
add(40808, 'Zwangsladung Speicher', 'System', '', 'raw', 'R')
add(40814, 'Offset T7', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40815, 'Offset T8', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40816, 'Offset T9', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40817, 'Offset T10', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40818, 'Offset T11', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40819, 'Offset 1T1', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40820, 'Offset T12', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40821, 'Offset T13', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40822, 'Offset 2T1', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40823, 'Offset 3T1', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40824, 'Offset 4T1', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40825, 'Offset 5T1', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40826, 'Offset 6T1', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40827, 'Offset 7T1', 'Diagnose', 'C', 'x0.1', 'R/W')
add(40828, 'Timeout ext. Boiler', 'System', 'min', 'x1', 'R/W')
add(40829, 'Min. RL Kessel', 'System', 'C', 'x1', 'R/W')
add(40830, 'Anlagennummer', 'System', '', 'raw', 'R/W')
add(40831, 'Nur ext. Energie bei AUS/FS', 'System', '0=Nein 1=Ja', 'raw', 'R/W')
add(40832, 'Ext. Energie und FW parallel', 'System', '0=Nein 1=Ja', 'raw', 'R/W')
add(40833, 'Solltemp. Legionellen Boiler 1', 'Boiler', 'C', 'x1', 'R/W')
add(40834, 'VL-Temp. Legionellen Boiler 1', 'Boiler', 'C', 'x1', 'R/W')
add(40835, 'Solltemp. Legionellen Boiler 2', 'Boiler', 'C', 'x1', 'R/W')
add(40836, 'VL-Temp. Legionellen Boiler 2', 'Boiler', 'C', 'x1', 'R/W')
add(40837, 'Hysterese Zirkulation', 'Zirkulation', 'C', 'x0.1', 'R/W')
add(40838, 'Legionellenzirkulation Boiler 1', 'Boiler', '0=Nein 1=Ja', 'raw', 'R/W')
add(40839, 'Legionellenzirkulation Boiler 2', 'Boiler', '0=Nein 1=Ja', 'raw', 'R/W')
add(40840, 'Startzeit Legionellenladung B1', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40841, 'Startzeit Legionellenladung B2', 'Boiler', 'hhmm', 'raw', 'R/W')
add(40842, '(Reserviert)', 'System', '', 'raw', 'R/W')
add(40843, 'BT Pairing Code', 'System', '', 'raw', 'R/W')
for hk in range(8):
    add(40844 + hk, f'Tagkorrektur Heizkreis {hk}', f'Heizkreis{hk}', 'C', 'x0.1', 'R/W')
add(40852, 'Ventilsynchronisation', 'System', '', 'raw', 'R/W')
add(40853, 'Funktion ComA', 'System', '', 'raw', 'R/W')
add(40854, 'Funktion ComB', 'System', '', 'raw', 'R/W')
add(40855, 'Funktion ComC', 'System', '', 'raw', 'R/W')
add(40856, 'Zubringpumpe nur mit FW aktiv', 'Ferwaerme', '0=Nein 1=Ja', 'raw', 'R/W')
for hk in range(8):
    add(40857 + hk, f'Fernbedienung per Bus HK{hk}', f'Heizkreis{hk}', '0=Nein 1=Ja', 'raw', 'R/W')
add(40865, 'Anzahl Subregler', 'System', '', 'raw', 'R/W')
add(40866, 'Handbetrieb Pumpe Boiler 1', 'Boiler', '0=Aus 1=Ein 2=Auto', 'raw', 'R/W')
add(40867, 'Handbetrieb Pumpe Boiler 2', 'Boiler', '0=Aus 1=Ein 2=Auto', 'raw', 'R/W')
for hk in range(8):
    add(40868 + hk, f'Laufzeit Ventil Heizkreis {hk}', f'Heizkreis{hk}', 's', 'x1', 'R/W')
add(40876, 'COM D Baudrate', 'System', '', 'raw', 'R/W')
for i in range(40877, 40920):
    add(i, f'Config FBS/HKM/PWM ({i})', 'System', '', 'raw', 'R/W')
add(40944, 'C-Max. Drehzahl Pumpe', 'System', '%', 'raw', 'R/W')
add(40945, 'D-Max. Drehzahl Pumpe', 'System', '%', 'raw', 'R/W')
add(40946, 'B-Max. Drehzahl Pumpe', 'System', '%', 'raw', 'R/W')
for i in range(1, 8):
    add(40946 + i, f'{i}-Max. Drehzahl Pumpe HKM{i}', 'System', '%', 'raw', 'R/W')
for i in range(40920, 40944):
    add(i, f'Regelart/Param ({i})', 'System', '', 'raw', 'R/W')
add(40954, 'FWM Solltemperatur', 'Ferwaerme', 'C', 'x1', 'R/W')
add(40955, '(reserviert)', 'System', '', 'raw', 'R/W')
add(40956, 'P-Bereich Basis C', 'System', 'C', 'x1', 'R/W')
add(40957, 'P-Bereich Basis D', 'System', 'C', 'x1', 'R/W')
for i in range(40958, 40966):
    add(i, f'P-Bereich ({i})', 'System', 'C', 'x1', 'R/W')
for i in range(40966, 40975):
    add(i, f'I-Faktor Pumpe ({i})', 'System', '', 'raw', 'R/W')
for i in range(40975, 41000):
    add(i, f'Res_para ({i})', 'System', '', 'raw', 'R/W')

# 41000-41110
for i in range(41000, 41014):
    add(i, f'Res_para ({i})', 'System', '', 'raw', 'R/W')
add(41014, 'C-PWM Pumpe (Klemme 2)', 'Diagnose', '%', 'raw', 'R')
add(41015, 'D-PWM Pumpe (Klemme 3)', 'Diagnose', '%', 'raw', 'R')
add(41016, 'B-PWM Pumpe (Klemme 1)', 'Diagnose', '%', 'raw', 'R')
for i in range(1, 8):
    add(41017 + i - 1, f'{i}-PWM Pumpe HKM{i}', 'Diagnose', '%', 'raw', 'R')
for i in range(41024, 41054):
    add(i, f'Istwert Reserve ({i})', 'Diagnose', '', 'raw', 'R')
add(41054, 'C-berechn. Drehzahl', 'Diagnose', '%', 'raw', 'R')
add(41055, 'D-berechn. Drehzahl', 'Diagnose', '%', 'raw', 'R')
add(41056, 'A-berechn. Drehzahl', 'Diagnose', '%', 'raw', 'R')
for i in range(1, 8):
    add(41057 + i - 1, f'{i}-berechn. Drehzahl Pumpe', 'Diagnose', '%', 'raw', 'R')
for i in range(1, 8):
    add(41064 + i - 1, f'{i}-berechn. Stellung Mischer', 'Diagnose', '%', 'raw', 'R')
for i in range(41071, 41078):
    add(i, f'Istwert Reserve ({i})', 'Diagnose', '', 'raw', 'R')
add(41078, 'Ventilstellung FW Ventil', 'Ferwaerme', '%', 'raw', 'R')
add(41079, 'B-Ventilstellung', 'Ferwaerme', '%', 'raw', 'R')
for i in range(1, 8):
    add(41080 + i - 1, f'{i}-Ventilstellung HKM{i}', 'Ferwaerme', '%', 'raw', 'R')
add(41087, 'B-Solltemp. Raum', 'System', 'C', 'x1', 'R')
for i in range(1, 8):
    add(41088 + i - 1, f'{i}-Solltemp. Raum', 'System', 'C', 'x1', 'R')
add(41097, 'FWM Isttemp. WW', 'Ferwaerme', 'C', 'x1', 'R')
add(41098, 'FWM Freigabe Modul', 'Ferwaerme', '', 'raw', 'R')
add(41099, 'FWM Drehzahl Pumpe', 'Ferwaerme', '%', 'raw', 'R')
add(41100, 'FWM Status Pumpe', 'Ferwaerme', '', 'raw', 'R')
add(41101, 'FWM Uebertemp. WW', 'Ferwaerme', '', 'raw', 'R')
for i in range(41102, 41105):
    add(i, f'Reserve ({i})', 'System', '', 'raw', 'R')
add(41103, 'Status Mischer Mengenreg. Speicher 1', 'System', '', 'raw', 'R')
add(41104, 'Status Mischer Mengenreg. Speicher 2', 'System', '', 'raw', 'R')
for i in range(41105, 41130):
    add(i, f'Reserve ({i})', 'System', '', 'raw', 'R')

# Zaehler 1 (42731-42768)
add(42731, 'Zaehler 1 Waermemenge HIGH', 'Zaehler1', '', 'raw', 'R')
add(42732, 'Zaehler 1 Waermemenge LOW -> 32bit /10 = kWh', 'Zaehler1', '0.1kWh', 'raw', 'R')
add(42733, 'Zaehler 1 Volumen HIGH', 'Zaehler1', '', 'raw', 'R')
add(42734, 'Zaehler 1 Volumen LOW -> 32bit = Liter', 'Zaehler1', 'l', 'raw', 'R')
add(42735, 'Zaehler 1 Leistung HIGH', 'Zaehler1', '', 'raw', 'R')
add(42736, 'Zaehler 1 Leistung LOW -> 32bit = Watt', 'Zaehler1', 'W', 'raw', 'R')
add(42737, 'Zaehler 1 Stichtagszaehlerstand HIGH', 'Zaehler1', '', 'raw', 'R')
add(42738, 'Zaehler 1 Stichtagszaehlerstand LOW', 'Zaehler1', '', 'raw', 'R')
add(42739, 'Zaehler 1 Seriennummer HIGH', 'Zaehler1', '', 'raw', 'R')
add(42740, 'Zaehler 1 Seriennummer LOW', 'Zaehler1', '', 'raw', 'R')
add(42741, 'Zaehler 1 Durchfluss long HIGH', 'Zaehler1', '', 'raw', 'R')
add(42742, 'Zaehler 1 Durchfluss long LOW -> l/h', 'Zaehler1', 'l/h', 'raw', 'R')
add(42743, 'Zaehler 1 Impulseingang A HIGH', 'Zaehler1', '', 'raw', 'R')
add(42744, 'Zaehler 1 Impulseingang A LOW', 'Zaehler1', '', 'raw', 'R')
add(42745, 'Zaehler 1 Fehleranzeige', 'Zaehler1', '', 'raw', 'R')
add(42746, 'Zaehler 1 Durchfluss int', 'Zaehler1', 'l/h', 'raw', 'R')
add(42747, 'Zaehler 1 Ruecklauftemp.', 'Zaehler1', 'C', 'x0.01', 'R')
add(42748, 'Zaehler 1 Vorlauftemp.', 'Zaehler1', 'C', 'x0.01', 'R')
add(42749, 'Zaehler 1 Spreizung', 'Zaehler1', 'C', 'x0.01', 'R')
add(42750, 'Zaehler 1 Betriebstage', 'Zaehler1', 'Tage', 'raw', 'R')
add(42751, 'Zaehler 1 Fehltage', 'Zaehler1', 'Tage', 'raw', 'R')
add(42752, 'Zaehler 1 Impulseingang B HIGH', 'Zaehler1', '', 'raw', 'R')
add(42753, 'Zaehler 1 Impulseingang B LOW', 'Zaehler1', '', 'raw', 'R')
add(42754, 'Zaehler 1 Tarif 1 HIGH', 'Zaehler1', '', 'raw', 'R')
add(42755, 'Zaehler 1 Tarif 1 LOW -> kWh', 'Zaehler1', 'kWh', 'raw', 'R')
add(42756, 'Zaehler 1 Tariflimit 1 HIGH', 'Zaehler1', '', 'raw', 'R')
add(42757, 'Zaehler 1 Tariflimit 1 LOW', 'Zaehler1', 'C', 'raw', 'R')
add(42758, 'Zaehler 1 Tarif 2 HIGH', 'Zaehler1', '', 'raw', 'R')
add(42759, 'Zaehler 1 Tarif 2 LOW -> kWh', 'Zaehler1', 'kWh', 'raw', 'R')
add(42760, 'Zaehler 1 Tariflimit 2 HIGH', 'Zaehler1', '', 'raw', 'R')
add(42761, 'Zaehler 1 Tariflimit 2 LOW', 'Zaehler1', 'C', 'raw', 'R')
add(42762, 'Zaehler 1 Tarif 3 HIGH', 'Zaehler1', '', 'raw', 'R')
add(42763, 'Zaehler 1 Tarif 3 LOW -> kWh', 'Zaehler1', 'kWh', 'raw', 'R')
add(42764, 'Zaehler 1 Tariflimit 3 HIGH', 'Zaehler1', '', 'raw', 'R')
add(42765, 'Zaehler 1 Tariflimit 3 LOW', 'Zaehler1', 'C', 'raw', 'R')
add(42766, 'Zaehler 1 HerstellerID', 'Zaehler1', '', 'raw', 'R')
add(42767, 'Zaehler 1 StatusByte', 'Zaehler1', '', 'raw', 'R')
add(42768, 'Zaehler 1 Version', 'Zaehler1', '', 'raw', 'R')

# ─── Integration-Mapping ──────────────────────────────────────────────────────
INTEGRATION = {
    40600: 'sensor: T6 Aussentemperatur',
    40601: 'sensor: T7 RL Primaer',
    40602: 'sensor: T8 VL Sekundaer',
    40603: 'sensor: T11 RL Sekundaer',
    40604: 'sensor: VL Soll Sekundaer',
    40605: 'sensor: Max RL Primaer',
    40606: 'sensor: Status Uebergabestation',
    40610: 'sensor: VL HK0 Ist',
    40611: 'sensor: Soll HK0',
    40612: 'sensor: Raumsoll HK0',
    40613: 'sensor: Raumtemp HK0',
    40616: 'binary_sensor: Pumpe HK0',
    40617: 'sensor: Status HK0',
    40618: 'sensor: Mischer HK0',
    40620: 'sensor: VL HK1 Ist',
    40621: 'sensor: Soll HK1',
    40622: 'sensor: Raumsoll HK1',
    40623: 'sensor: Raumtemp HK1',
    40626: 'binary_sensor: Pumpe HK1',
    40627: 'sensor: Status HK1',
    40628: 'sensor: Mischer HK1',
    40630: 'sensor: VL HK2 Ist',
    40631: 'sensor: Soll HK2',
    40632: 'sensor: Raumsoll HK2',
    40633: 'sensor: Raumtemp HK2',
    40636: 'binary_sensor: Pumpe HK2',
    40637: 'sensor: Status HK2',
    40638: 'sensor: Mischer HK2',
    40640: 'sensor: VL HK3 Ist',
    40641: 'sensor: Soll HK3',
    40642: 'sensor: Raumsoll HK3',
    40643: 'sensor: Raumtemp HK3',
    40646: 'binary_sensor: Pumpe HK3',
    40647: 'sensor: Status HK3',
    40648: 'sensor: Mischer HK3',
    40690: 'sensor: T9 Speicher 1 oben',
    40691: 'sensor: T10 Speicher 1 unten',
    40692: 'sensor: Soll VL Boiler 1',
    40693: 'sensor: Status Boilerkreis 1',
    40694: 'binary_sensor: Pumpe Boiler 1',
    40700: 'sensor: Temp VL Lademodul 1',
    40701: 'sensor: Temp VL Lademodul 2',
    40702: 'sensor: Temp Zirkulation 1',
    40703: 'sensor: Temp Zirkulation 2',
    40704: 'sensor: Einschalttemp Puffer',
    40705: 'sensor: Ausschalttemp Puffer',
    40706: 'sensor: Drehzahl Puffer',
    40707: 'sensor: Drehzahl Solar',
    40708: 'binary_sensor: Zubringpumpe',
    40709: 'sensor: Ventilstellung',
    40710: 'sensor: Status SD-Card',
    40711: 'sensor: Softwareversion',
    40712: 'sensor: Hydraulikvariante',
    40716: 'sensor: Uhrzeit',
    40717: 'sensor: Wochentag',
    40718: 'sensor: Tag',
    40719: 'sensor: Monat',
    40720: 'sensor: Jahr',
    40721: 'sensor: Status Pumpe LM1',
    40722: 'sensor: Status Mischer LM1',
    40723: 'sensor: Status Pumpe LM2',
    40724: 'sensor: Status Mischer LM2',
    40726: 'sensor: Reset Counter',
    40728: 'sensor: Aussentemp Mittel',
    40729: 'sensor: Aussentemp Mittel Langzeit',
    40730: 'sensor: Waermemenge (32bit HIGH - zusammen mit 40731)',
    40731: 'sensor: Waermemenge (32bit LOW -> /10 kWh)',
    40734: 'sensor: Leistung FW (32bit HIGH - zusammen mit 40735)',
    40735: 'sensor: Leistung FW (32bit LOW -> W)',
    40012: 'sensor/number: Offset Aussentemp',
    40023: 'number: Volle Nachtabsenkung',
    40024: 'number: Keine Nachtabsenkung',
    40028: 'number: VL bei Frost',
    40029: 'sensor: Frost Aussentemp',
    40030: 'select: Ausheizprogramm',
    40049: 'number: Stationserhöhung',
    40050: 'number: Handbetrieb Ventil',
    40053: 'sensor: Leistungsbegrenzung',
    40215: 'select: Funktion WUEST',
    40240: 'select: Betriebsmodus HK0',
    40241: 'select: Betriebsmodus HK1',
    40242: 'select: Betriebsmodus HK2',
    40243: 'select: Betriebsmodus HK3',
}


def get_interp(re, rv):
    if rv is None:
        return 'n/v'
    if rv in SENTINEL:
        return 'SENTINEL'
    s = re['skalierung']
    if s == 'x0.1':
        v = rv - 65536 if rv > 32767 else rv
        return f'{v / 10:.1f}'
    elif s == 'x0.01':
        v = rv - 65536 if rv > 32767 else rv
        return f'{v / 100:.2f}'
    elif s == 'x1':
        return str(rv)
    else:
        return str(rv)


# ─── Excel bauen ──────────────────────────────────────────────────────────────
wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Modbus Register'

C_HDR  = 'FF1F4E79'
C_FW   = 'FFDCE6F1'
C_HK   = 'FFE2EFDA'
C_BOIL = 'FFFCE4D6'
C_SYS  = 'FFF2F2F2'
C_DIAG = 'FFFFF2CC'
C_WUEST= 'FFE8D5F5'
C_ZEIT = 'FFEAF4FF'
C_ZAEH = 'FFFFE0B2'
C_PUFF = 'FFFCE4D6'
C_YINT = 'FFD6E4BC'
C_SENT = 'FFFFCCCC'
C_UNAVL= 'FFE0E0E0'

KAT_CLR = {
    'Ferwaerme': C_FW, 'Waermezaehler': C_FW,
    'Heizkreis0': C_HK, 'Heizkreis1': C_HK, 'Heizkreis2': C_HK, 'Heizkreis3': C_HK,
    'Heizkreis4': C_HK, 'Heizkreis5': C_HK, 'Heizkreis6': C_HK, 'Heizkreis7': C_HK,
    'Boiler': C_BOIL, 'Puffer': C_PUFF, 'Lademodul': C_PUFF,
    'Zirkulation': C_PUFF, 'Solar': C_PUFF,
    'System': C_SYS, 'Konfiguration': C_SYS,
    'Diagnose': C_DIAG,
    'WUEST': C_WUEST,
    'Zeitprogramm': C_ZEIT,
    'Zaehler1': C_ZAEH,
}

headers = [
    'PDF-Register', 'pymodbus-Adresse', 'Bezeichnung (PDF)', 'Kategorie',
    'Einheit', 'Skalierung', 'R/W', 'Rohwert (Scan)', 'Wert interpretiert',
    'SENTINEL?', 'In Integration?', 'Entity-Typ / data_key', 'Benutzer-Korrekturen'
]
ws.append(headers)
for col, _ in enumerate(headers, 1):
    c = ws.cell(row=1, column=col)
    c.font = Font(bold=True, color='FFFFFFFF', size=10)
    c.fill = PatternFill('solid', fgColor=C_HDR)
    c.alignment = Alignment(horizontal='center', wrap_text=True)

col_w = [15, 18, 52, 14, 12, 12, 6, 14, 16, 10, 14, 38, 30]
for i, w in enumerate(col_w, 1):
    ws.column_dimensions[get_column_letter(i)].width = w

ws.freeze_panes = 'A2'
ws.auto_filter.ref = 'A1:M1'

row_num = 2
for re in registers:
    reg  = re['reg']
    addr = reg - 40000
    rv   = raw_val(addr)
    avail = rv is not None
    is_s  = rv in SENTINEL if rv is not None else False
    interp = get_interp(re, rv)
    integ = INTEGRATION.get(reg)
    in_i  = 'Ja' if integ else 'Nein'
    entity = integ if integ else ''

    ws.append([
        reg, addr, re['desc'], re['kat'], re['einheit'],
        re['skalierung'], re['rw'],
        rv if avail else 'n/v',
        interp, 'SENTINEL' if is_s else '',
        in_i, entity, ''
    ])

    kat_clr = KAT_CLR.get(re['kat'], C_SYS)
    for col in range(1, len(headers) + 1):
        c = ws.cell(row=row_num, column=col)
        c.font = Font(size=9)
        c.alignment = Alignment(vertical='center', wrap_text=(col in (3, 12, 13)))
        if not avail:
            c.fill = PatternFill('solid', fgColor=C_UNAVL)
        elif is_s:
            c.fill = PatternFill('solid', fgColor=C_SENT)
        elif col == 11 and in_i == 'Ja':
            c.fill = PatternFill('solid', fgColor=C_YINT)
        else:
            c.fill = PatternFill('solid', fgColor=kat_clr)
    ws.row_dimensions[row_num].height = 14
    row_num += 1

# ─── Sheet 2: Kurzuebersicht wichtige Istwerte ────────────────────────────────
ws2 = wb.create_sheet('Wichtige Istwerte')

def h(cell_ref, txt):
    ws2[cell_ref].value = txt
    ws2[cell_ref].font = Font(bold=True)

h('A1', 'PDF-Reg'); h('B1', 'Bezeichnung'); h('C1', 'Rohwert')
h('D1', 'Wert'); h('E1', 'Einheit'); h('F1', 'In Integration')

highlights = [
    (40600, 'T6 Aussentemperatur', 'x0.1', 'C'),
    (40601, 'T7 RL Primaer Ist', 'x0.1', 'C'),
    (40602, 'T8 VL Sekundaer Ist', 'x0.1', 'C'),
    (40603, 'T11 RL Sekundaer Ist', 'x0.1', 'C'),
    (40604, 'Soll VL Sekundaer', 'x0.1', 'C'),
    (40605, 'Max RL Primaer', 'x0.1', 'C'),
    (40606, 'Status Uebergabestation', 'raw', ''),
    (40609, 'Register 40609 (raw)', 'raw', ''),
    (40620, 'VL HK1', 'x0.1', 'C'),
    (40621, 'Soll HK1', 'x0.1', 'C'),
    (40622, 'Raumsoll HK1', 'x0.1', 'C'),
    (40623, 'Raumtemp HK1', 'x0.1', 'C'),
    (40626, 'Pumpe HK1', 'raw', ''),
    (40627, 'Status HK1', 'raw', ''),
    (40628, 'Mischer HK1', 'raw', ''),
    (40690, 'T9 Speicher1 oben', 'x0.1', 'C'),
    (40691, 'T10 Speicher1 unten', 'x0.1', 'C'),
    (40706, 'Drehzahl Puffer', 'raw', '%'),
    (40707, 'Drehzahl Solar', 'raw', '%'),
    (40708, 'Zubringpumpe', 'raw', ''),
    (40709, 'Ventilstellung', 'raw', '%'),
    (40711, 'Softwareversion', 'raw', ''),
    (40712, 'Hydraulikvariante', 'raw', ''),
    (40716, 'Uhrzeit', 'raw', 'hhmm'),
    (40717, 'Tag', 'raw', ''),
    (40718, 'Monat', 'raw', ''),
    (40720, 'Jahr', 'raw', ''),
    (40726, 'Reset Counter', 'raw', ''),
    (40728, 'Aussentemp Mittel', 'x0.1', 'C'),
    (40729, 'Aussentemp Mittel Langzeit', 'x0.1', 'C'),
]

ws2.append(['', '', '', '', '', ''])
ws2.append(['=== 32-bit intern ===', '', '', '', '', ''])
wm32   = r32(40730)
vol32  = r32(40732)
leis32 = r32(40734)
ws2.append([40730, 'Waermemenge intern', wm32,
            f'{wm32 / 10:.1f}' if wm32 is not None else 'n/v', 'kWh', 'Ja'])
ws2.append([40732, 'Volumen intern', vol32,
            vol32 if vol32 is not None else 'n/v', 'l', 'Nein'])
ws2.append([40734, 'Leistung intern', leis32,
            leis32 if leis32 is not None else 'n/v', 'W', 'Ja'])
ws2.append(['', '', '', '', '', ''])

for (preg, nm, skal, einh) in highlights:
    a = preg - 40000
    rv = raw_val(a)
    if rv is not None:
        if skal == 'x0.1':
            interp = (rv - 65536) / 10 if rv > 32767 else rv / 10
        elif skal == 'x0.01':
            interp = (rv - 65536) / 100 if rv > 32767 else rv / 100
        else:
            interp = rv
        in_i = 'Ja' if preg in INTEGRATION else 'Nein'
        ws2.append([preg, nm, rv, interp, einh, in_i])

for col, w in zip(['A', 'B', 'C', 'D', 'E', 'F'], [14, 36, 12, 14, 10, 18]):
    ws2.column_dimensions[col].width = w

wb.save('C:/Users/rolfl/claudecode/Schneid/Schneid_MR12_Register.xlsx')
print(f'Fertig! {row_num - 1} Register in Excel.')
print(f'Waermemenge: {wm32 / 10:.1f} kWh')
print(f'Volumen:     {vol32} l')
print(f'Leistung:    {leis32} W')
