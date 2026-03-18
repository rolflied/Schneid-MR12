"""Konstanten für die Schneid MR-12 Integration."""

DOMAIN = "schneid_mr12"

DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30

CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_HEATING_CIRCUITS = "heating_circuits"
CONF_READ_ONLY = "read_only"

# Default: Heizkreis 0 + 1 aktiv; vollständiger Schreibzugriff
DEFAULT_HEATING_CIRCUITS: list[str] = ["0", "1"]
DEFAULT_READ_ONLY = False

# Modbus-Register-Basisadresse: PDF-Register - MODBUS_BASE = pymodbus-Adresse
MODBUS_BASE = 40000

# ─── Registeradressen (PDF-Register - MODBUS_BASE) ───────────────────────────

# Haupttemperaturen / Übergabestation (Block 600)
REG_T6_AUSSENTEMP       = 600   # T6 Außentemperatur, x,x°C
REG_T7_RL_PRIMAER       = 601   # T7 RL Primär, x,x°C
REG_T8_VL_SEKUNDAER     = 602   # T8 VL Sekundär, x,x°C
REG_T11_RL_SEKUNDAER    = 603   # T11 RL Sekundär, x,x°C
REG_VL_SOLL_SEKUNDAER   = 604   # Solltemperatur VL Sekundär, x,x°C
REG_MAX_RL_PRIMAER      = 605   # Max. Rücklauftemp. primär, x,x°C
REG_STATUS_UEBERGABE    = 606   # Status Übergabestation

# Heizkreis 0 (Block 610)
REG_VL_HK0          = 610   # VL Heizkreis 0, x,x°C
REG_SOLL_HK0        = 611   # Solltemperatur Heizkreis 0, x,x°C
REG_RAUMSOLL_HK0    = 612   # Raumsolltemperatur Heizkreis 0, x,x°C
REG_RAUMTEMP_HK0    = 613   # Raumtemperatur Heizkreis 0, x,x°C
REG_PUMPE_HK0       = 616   # Pumpe Heizkreis 0
REG_STATUS_HK0      = 617   # Status Heizkreis 0
REG_MISCHER_HK0     = 618   # Status Mischer Heizkreis 0

# Heizkreis 1 (Block 620)
REG_VL_HK1          = 620
REG_SOLL_HK1        = 621
REG_RAUMSOLL_HK1    = 622
REG_RAUMTEMP_HK1    = 623
REG_PUMPE_HK1       = 626
REG_STATUS_HK1      = 627
REG_MISCHER_HK1     = 628

# Boiler / Warmwasserspeicher (Block 690)
REG_T9_SPEICHER1_OBEN   = 690   # T9 Speicher 1 oben, x,x°C
REG_T10_SPEICHER1_UNTEN = 691   # T10 Speicher 1 unten, x,x°C
REG_SOLL_VL_BOILER1     = 692   # Solltemperatur VL Boiler 1, x,x°C
REG_STATUS_BOILER1      = 693   # Status Boilerkreis 1
REG_PUMPE_BOILER1       = 694   # Pumpe Boiler 1
REG_T12_SPEICHER2_OBEN  = 695   # T12 Speicher 2 oben, x,x°C
REG_T13_SPEICHER2_UNTEN = 696   # T13 Speicher 2 unten, x,x°C
REG_SOLL_VL_BOILER2     = 697   # Solltemperatur VL Boiler 2, x,x°C
REG_STATUS_BOILER2      = 698   # Status Boilerkreis 2
REG_PUMPE_BOILER2       = 699   # Pumpe Boiler 2

# Lademodul / Puffer / Ventil (Block 700)
REG_VL_LADEMODUL1       = 700   # Temp. VL Lademodul 1, x,x°C
REG_VL_LADEMODUL2       = 701   # Temp. VL Lademodul 2, x,x°C
REG_TEMP_ZIRKULATION1   = 702   # Temp. Zirkulation 1, x,x°C
REG_TEMP_ZIRKULATION2   = 703   # Temp. Zirkulation 2, x,x°C
REG_EINSCHALT_PUFFER    = 704   # Einschalttemperatur Puffer, x,x°C
REG_AUSSCHALT_PUFFER    = 705   # Ausschalttemperatur Puffer, x,x°C
REG_DREHZAHL_PUFFER     = 706   # Drehzahl Puffer, %
REG_DREHZAHL_SOLAR      = 707   # Drehzahl Solar, %
REG_ZUBRINGPUMPE        = 708   # Zubringpumpe
REG_VENTILSTELLUNG      = 709   # Ventilstellung, %

# Diagnose / Info (Block 710)
REG_STATUS_SDCARD       = 710   # Status SDCard in Slot
REG_SOFTWARE_VERSION    = 711   # Version Software
REG_HYDRAULIKVARIANTE   = 712   # Hydraulikvariante
REG_ZIRKULATIONSPUMPE1  = 714   # Zirkulationspumpe 1
REG_ZIRKULATIONSPUMPE2  = 715   # Zirkulationspumpe 2
REG_UHRZEIT             = 716   # Uhrzeit Regler hhmm
REG_TAG                 = 717   # Tag Regler
REG_MONAT               = 718   # Monat Regler
REG_WOCHENTAG           = 719   # Wochentag Regler
REG_JAHR                = 720   # Jahr Regler
REG_STATUS_PUMPE_LM1    = 721   # Status Pumpe Lademodul 1
REG_STATUS_MISCHER_LM1  = 722   # Status Mischer Lademodul 1
REG_STATUS_PUMPE_LM2    = 723   # Status Pumpe Lademodul 2
REG_STATUS_MISCHER_LM2  = 724   # Status Mischer Lademodul 2
REG_RESET_COUNTER       = 726   # Reset Counter

# Außentemperatur Mittelwerte (Block 728)
REG_AUSSENTEMP_MITTEL    = 728  # Außentemp. Mittel, x,x°C
REG_AUSSENTEMP_MITTEL_LZ = 729  # Außentemp. Mittel Langzeit, x,x°C

# Wärmezähler integriert – 32-Bit-Werte (je High-/Low-Word)
REG_WAERMEMENGE_H   = 730   # Wärmemenge HIGH-Word (Einheit: 0,1 kWh)
REG_WAERMEMENGE_L   = 731   # Wärmemenge LOW-Word
REG_VOLUMEN_H       = 732   # Volumen HIGH-Word (l)
REG_VOLUMEN_L       = 733   # Volumen LOW-Word
REG_LEISTUNG_H      = 734   # Leistung HIGH-Word (W)
REG_LEISTUNG_L      = 735   # Leistung LOW-Word

# HK1 Heizkurve – Sollwerte (R/W, Einheit: °C)
REG_HK1_VL_SOLL_20AT   = 117   # HK1 VL Soll bei +20°C AT
REG_HK1_VL_SOLL_5AT    = 118   # HK1 VL Soll bei +5°C AT
REG_HK1_VL_SOLL_M10AT  = 119   # HK1 VL Soll bei -10°C AT
REG_HK1_MAX_VL          = 120   # HK1 Max. Vorlauftemperatur
REG_HK1_MIN_VL          = 121   # HK1 Min. Vorlauftemperatur

# Boiler-Sollwerte (R/W)
REG_BOILERSOLL1         = 80    # Boilersolltemp. 1, °C
REG_BOILERMIN1          = 81    # Boilerminimaltemp. 1, °C
REG_BOILERAUS1          = 82    # Boilerausschalttemp. 1, °C
REG_BOILERLADESOLL1     = 83    # Boilerladetemp. Soll 1, °C
REG_BOILERLADEMIN1      = 84    # Boilerladetemp. Min 1, °C

# Systemparameter (R/W)
REG_OFFSET_AUSSENTEMP   = 12    # Offset Außentemperatur, x,x°C
REG_VOLLE_NACHT         = 23    # Volle Nachtabsenkung, °C
REG_KEINE_NACHT         = 24    # Keine Nachtabsenkung, °C
REG_VL_BEI_FROST        = 28    # Vorlauftemp. bei Frost, °C
REG_FROST_AUSSENTEMP    = 29    # Frostschutztemp. Außen, °C
REG_AUSHEIZPROGRAMM     = 30    # Ausheizprogramm
REG_STATIONSERHÖHUNG    = 49    # Stationserhöhung, °C
REG_HANDBETRIEB_VENTIL  = 50    # Handbetrieb Prim.ventil
REG_LEISTUNGSBEGRENZUNG = 53    # Leistungsbegrenzung Ja/Nein

# WÜST / Betriebsmodi (R/W)
REG_FUNKTION_WUEST      = 215   # FUNKTION WÜST
REG_BETRIEBSMODUS_HK0   = 240   # Betriebsmodus Kreis 0
REG_BETRIEBSMODUS_HK1   = 241   # Betriebsmodus Kreis 1
REG_BETRIEBSMODUS_HK2   = 242   # Betriebsmodus Kreis 2
REG_BETRIEBSMODUS_HK3   = 243   # Betriebsmodus Kreis 3

# FWM Solltemperatur (R/W)
REG_FWM_SOLL            = 954   # FWM Solltemperatur, °C

# Zähler 1 (externer Wärmemengenzähler, 32-Bit)
REG_Z1_WAERMEMENGE_H    = 2731
REG_Z1_WAERMEMENGE_L    = 2732
REG_Z1_LEISTUNG_H       = 2735
REG_Z1_LEISTUNG_L       = 2736
REG_Z1_DURCHFLUSS_H     = 2741
REG_Z1_DURCHFLUSS_L     = 2742
REG_Z1_FEHLERANZEIGE    = 2745
REG_Z1_DURCHFLUSS_INT   = 2746
REG_Z1_RL_TEMP          = 2747  # x.xx°C
REG_Z1_VL_TEMP          = 2748  # x.xx°C
REG_Z1_SPREIZUNG        = 2749  # x.xx°C
REG_Z1_BETRIEBSTAGE     = 2750
REG_Z1_FEHLTAGE         = 2751

# ─── Enum-Maps ────────────────────────────────────────────────────────────────

STATUS_UEBERGABE = {
    0: "AUS",
    1: "EIN",
    2: "RL-Begrenzung",
    3: "Leistungsbegrenzung",
    4: "Handbetrieb",
}

STATUS_HEIZKREIS = {
    0:  "Pumpe AUS – Mischer steht",
    1:  "Pumpe EIN – Mischer steht",
    2:  "Pumpe EIN – Mischer AUF",
    3:  "Pumpe EIN – Mischer ZU",
    4:  "Pumpe AUS – Mischer AUF",
    5:  "Pumpe AUS – Mischer ZU",
    6:  "Fernbed. Hand: AUTO",
    7:  "Fernbed. Hand: TAG",
    8:  "Fernbed. Hand: NACHT",
    9:  "Automatik",
    10: "Fernbed. Hand: AUS/FS",
}

STATUS_MISCHER = {
    0: "Steht",
    1: "Auf",
    2: "Zu",
}

STATUS_BOILERKREIS = {
    0: "Hand: Boilerpumpe AUS",
    1: "Hand: Boilerpumpe EIN",
    9: "Automatik",
}

# Betriebsmodus für Heizkreise (Register 40240+)
BETRIEBSMODUS_HK_OPTIONS = {
    0: "AUS / Frostschutz",
    1: "Absenkbetrieb",
    2: "Heizbetrieb",
    3: "Zeitprogramm",
    4: "Partymodus",
    5: "Wahlschalter gilt (Standard)",
    6: "Pumpe AUS, Mischer steht",
}

# FUNKTION WÜST (Register 40215) – für die gesamte Übergabestation
FUNKTION_WUEST_OPTIONS = {
    0: "AUS / Frostschutz",
    1: "Nur Absenkbetrieb",
    2: "Nur Heizbetrieb",
    3: "Automatikbetrieb / Zeitprogramm",
    4: "Nur Boilerbetrieb",
    5: "Partymodus",
    6: "Wartung (Aus, kein Frostschutz!)",
}

HANDBETRIEB_VENTIL_OPTIONS = {
    0: "Ventil ZU",
    1: "Ventil AUF",
    2: "Ventil STOP",
    3: "Automatik",
}

AUSHEIZPROGRAMM_OPTIONS = {
    0: "AUS",
    1: "Alle Heizkreise",
    2: "Heizkreis 0",
    3: "Heizkreis 1",
    4: "Heizkreis 2",
    5: "Heizkreis 3",
}
