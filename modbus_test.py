"""Modbus-Test: liest alle Register-Blöcke der Schneid MR-12 aus."""

import asyncio
import inspect
from pymodbus.client import AsyncModbusTcpClient

HOST   = "192.168.5.14"
PORT   = 1504
SLAVE  = 1


def _u16s(v: int) -> float:
    return (v - 65536 if v > 32767 else v) / 10


def _u16s100(v: int) -> float:
    return (v - 65536 if v > 32767 else v) / 100


def _r32(regs, hi):
    return (regs[hi] << 16) | regs[hi + 1]


async def rhr(client, address, count):
    """Liest Holding-Register mit automatischer API-Erkennung."""
    for kw in (
        {"count": count, "slave": SLAVE},
        {"count": count, "unit": SLAVE},
        {"count": count},
    ):
        try:
            return await client.read_holding_registers(address, **kw)
        except TypeError:
            continue
    for kw in (
        {"slave": SLAVE},
        {"unit": SLAVE},
        {},
    ):
        try:
            return await client.read_holding_registers(address, count, **kw)
        except TypeError:
            continue
    raise RuntimeError("Keine kompatible pymodbus-Signatur")


async def main():
    print(f"Verbinde mit {HOST}:{PORT} Slave {SLAVE} ...")
    client = AsyncModbusTcpClient(host=HOST, port=PORT, timeout=10)
    connected = await client.connect()
    if not connected:
        print("FEHLER: Verbindung fehlgeschlagen!")
        return
    print("Verbunden.\n")

    # Signatur anzeigen
    sig = inspect.signature(client.read_holding_registers)
    print(f"pymodbus read_holding_registers Signatur: {sig}\n")
    print("=" * 60)

    # ── Block 1a: 40600-40629 ──────────────────────────────────────
    print("\n[Block 1a] 40600–40629 (Haupttemps + HK0 + HK1)")
    r = await rhr(client, 600, 30)
    if r.isError():
        print(f"  FEHLER: {r}")
    else:
        regs = r.registers
        print(f"  T6  Außentemperatur:     {_u16s(regs[0]):.1f} °C")
        print(f"  T7  RL Primär Ist:       {_u16s(regs[1]):.1f} °C")
        print(f"  T8  VL Sekundär Ist:     {_u16s(regs[2]):.1f} °C")
        print(f"  T11 RL Sekundär Ist:     {_u16s(regs[3]):.1f} °C")
        print(f"  VL Soll Sekundär:        {_u16s(regs[4]):.1f} °C")
        print(f"  Max RL Primär:           {_u16s(regs[5]):.1f} °C")
        print(f"  Status Übergabe:         {regs[6]}")
        print(f"  --- Heizkreis 0 ---")
        print(f"  VL HK0 Ist:              {_u16s(regs[10]):.1f} °C")
        print(f"  VL HK0 Soll:             {_u16s(regs[11]):.1f} °C")
        print(f"  Raumsoll HK0:            {_u16s(regs[12]):.1f} °C")
        print(f"  Raumtemp HK0:            {_u16s(regs[13]):.1f} °C")
        print(f"  Pumpe HK0:               {regs[16]}")
        print(f"  Status HK0:              {regs[17]}")
        print(f"  Mischer HK0:             {regs[18]}")
        print(f"  --- Heizkreis 1 ---")
        print(f"  VL HK1 Ist:              {_u16s(regs[20]):.1f} °C")
        print(f"  VL HK1 Soll:             {_u16s(regs[21]):.1f} °C")
        print(f"  Raumsoll HK1:            {_u16s(regs[22]):.1f} °C")
        print(f"  Raumtemp HK1:            {_u16s(regs[23]):.1f} °C")
        print(f"  Pumpe HK1:               {regs[26]}")
        print(f"  Status HK1:              {regs[27]}")
        print(f"  Mischer HK1:             {regs[28]}")

    # ── Block 1b: 40630-40648 ──────────────────────────────────────
    print("\n[Block 1b] 40630–40648 (HK2 + HK3)")
    r = await rhr(client, 630, 19)
    if r.isError():
        print(f"  FEHLER (HK2/HK3 ggf. nicht vorhanden): {r}")
    else:
        regs = r.registers
        print(f"  VL HK2 Ist:  {_u16s(regs[0]):.1f}  Soll: {_u16s(regs[1]):.1f}  Pumpe: {regs[6]}  Status: {regs[7]}")
        print(f"  VL HK3 Ist:  {_u16s(regs[10]):.1f}  Soll: {_u16s(regs[11]):.1f}  Pumpe: {regs[16]}  Status: {regs[17]}")

    # ── Block 2: 40690-40751 ───────────────────────────────────────
    print("\n[Block 2] 40690–40751 (Boiler + Pumpen + Wärmezähler)")
    r = await rhr(client, 690, 62)
    if r.isError():
        print(f"  FEHLER: {r}")
    else:
        regs = r.registers
        print(f"  T9  Speicher1 Oben:      {_u16s(regs[0]):.1f} °C")
        print(f"  T10 Speicher1 Unten:     {_u16s(regs[1]):.1f} °C")
        print(f"  VL Soll Boiler 1:        {_u16s(regs[2]):.1f} °C")
        print(f"  Status Boiler 1:         {regs[3]}")
        print(f"  Pumpe Boiler 1:          {regs[4]}")
        print(f"  T12 Speicher2 Oben:      {_u16s(regs[5]):.1f} °C")
        print(f"  T13 Speicher2 Unten:     {_u16s(regs[6]):.1f} °C")
        print(f"  VL Soll Boiler 2:        {_u16s(regs[7]):.1f} °C")
        print(f"  Status Boiler 2:         {regs[8]}")
        print(f"  Pumpe Boiler 2:          {regs[9]}")
        print(f"  VL Lademodul 1:          {_u16s(regs[10]):.1f} °C")
        print(f"  VL Lademodul 2:          {_u16s(regs[11]):.1f} °C")
        print(f"  Temp Zirkulation 1:      {_u16s(regs[12]):.1f} °C")
        print(f"  Temp Zirkulation 2:      {_u16s(regs[13]):.1f} °C")
        print(f"  Einschalt Puffer:        {_u16s(regs[14]):.1f} °C")
        print(f"  Ausschalt Puffer:        {_u16s(regs[15]):.1f} °C")
        print(f"  Drehzahl Puffer:         {regs[16]} %")
        print(f"  Drehzahl Solar:          {regs[17]} %")
        print(f"  Zubringpumpe:            {regs[18]}")
        print(f"  Ventilstellung:          {regs[19]} %")
        print(f"  Status SDCard:           {regs[20]}")
        print(f"  Softwareversion:         {regs[21]}")
        print(f"  Hydraulikvariante:       {regs[22]}")
        print(f"  Zirkulationspumpe 1:     {regs[24]}")
        print(f"  Zirkulationspumpe 2:     {regs[25]}")
        print(f"  Uhrzeit (hhmm):          {regs[26]}")
        print(f"  Tag/Monat/Jahr:          {regs[27]}.{regs[28]}.{regs[30]}")
        print(f"  Reset-Zähler:            {regs[36]}")
        print(f"  Außentemp Mittel:        {_u16s(regs[38]):.1f} °C")
        print(f"  Außentemp Mittel LZ:     {_u16s(regs[39]):.1f} °C")
        wm   = _r32(regs, 40) / 10
        vol  = _r32(regs, 42)
        pow_ = _r32(regs, 44)
        flow = _r32(regs, 50)
        print(f"  Wärmemenge Gesamt:       {wm:.1f} kWh")
        print(f"  Volumen:                 {vol} L")
        print(f"  Leistung:                {pow_} W")
        print(f"  Durchfluss:              {flow} l/h")
        print(f"  Fehleranzeige:           {regs[54]}")
        print(f"  RL Temp (Zähler):        {_u16s100(regs[56]):.2f} °C")
        print(f"  VL Temp (Zähler):        {_u16s100(regs[57]):.2f} °C")
        print(f"  Spreizung (Zähler):      {_u16s100(regs[58]):.2f} K")
        print(f"  Betriebstage:            {regs[59]}")
        print(f"  Fehltage:                {regs[60]}")

    # ── Block 3: 40012-40099 ───────────────────────────────────────
    print("\n[Block 3] 40012–40099 (Systemparameter)")
    r = await rhr(client, 12, 88)
    if r.isError():
        print(f"  FEHLER: {r}")
    else:
        regs = r.registers
        print(f"  Offset Außentemp:        {_u16s(regs[0]):.1f} °C  (reg 40012)")
        print(f"  Volle Nachtabsenkung:    {regs[11]} °C  (reg 40023)")
        print(f"  Keine Nachtabsenkung:    {regs[12]} °C  (reg 40024)")
        print(f"  VL bei Frost:            {regs[16]} °C  (reg 40028)")
        print(f"  Frost Außentemp:         {(regs[17] - 65536 if regs[17] > 32767 else regs[17])} °C  (reg 40029)")
        print(f"  Ausheizprogramm:         {regs[18]}      (reg 40030)")
        print(f"  Stationserhöhung:        {regs[37]} °C  (reg 40049)")
        print(f"  Handbetrieb Ventil:      {regs[38]}      (reg 40050)")
        print(f"  Leistungsbegrenzung:     {regs[41]}      (reg 40053)")
        print(f"  Boilersoll 1:            {regs[68]} °C  (reg 40080)")
        print(f"  Boilermin 1:             {regs[69]} °C  (reg 40081)")
        print(f"  Boileraus 1:             {regs[70]} °C  (reg 40082)")
        print(f"  Boilerladesoll 1:        {regs[71]} °C  (reg 40083)")
        print(f"  Boilerlademin 1:         {regs[72]} °C  (reg 40084)")

    # ── Block 4: 40215-40244 ───────────────────────────────────────
    print("\n[Block 4] 40215–40244 (Betriebsmodi)")
    r = await rhr(client, 215, 30)
    if r.isError():
        print(f"  FEHLER: {r}")
    else:
        regs = r.registers
        print(f"  Funktion WÜST:           {regs[0]}  (reg 40215)")
        print(f"  Betriebsmodus HK0:       {regs[25]} (reg 40240)")
        print(f"  Betriebsmodus HK1:       {regs[26]} (reg 40241)")
        print(f"  Betriebsmodus HK2:       {regs[27]} (reg 40242)")
        print(f"  Betriebsmodus HK3:       {regs[28]} (reg 40243)")

    # ── Block 5: 40954 ─────────────────────────────────────────────
    print("\n[Block 5] 40954 (FWM Solltemperatur)")
    r = await rhr(client, 954, 1)
    if r.isError():
        print(f"  FEHLER: {r}")
    else:
        print(f"  FWM Soll:                {r.registers[0]} °C")

    # ── Block 6: 42731-42751 ───────────────────────────────────────
    print("\n[Block 6] 42731–42751 (Zähler 1 ext.)")
    r = await rhr(client, 2731, 21)
    if r.isError():
        print(f"  FEHLER (Zähler 1 ggf. nicht vorhanden): {r}")
    else:
        regs = r.registers
        z1_wm   = _r32(regs, 0) / 10
        z1_pow  = _r32(regs, 4)
        z1_flow = _r32(regs, 10)
        print(f"  Z1 Wärmemenge:           {z1_wm:.1f} kWh")
        print(f"  Z1 Leistung:             {z1_pow} W")
        print(f"  Z1 Durchfluss:           {z1_flow} l/h")
        print(f"  Z1 RL Temp:              {_u16s100(regs[16]):.2f} °C")
        print(f"  Z1 VL Temp:              {_u16s100(regs[17]):.2f} °C")
        print(f"  Z1 Spreizung:            {_u16s100(regs[18]):.2f} K")
        print(f"  Z1 Betriebstage:         {regs[19]}")
        print(f"  Z1 Fehleranzeige:        {regs[14]}")

    print("\n" + "=" * 60)
    print("Test abgeschlossen.")
    client.close()


asyncio.run(main())
