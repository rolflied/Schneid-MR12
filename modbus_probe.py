"""Detailanalyse: testet Block 2+3 mit kleineren Chunks."""

import asyncio
from pymodbus.client import AsyncModbusTcpClient

HOST, PORT, SLAVE = "192.168.5.14", 1504, 1


async def rhr(client, address, count):
    for kw in ({"count": count, "device_id": SLAVE}, {"count": count}):
        try:
            return await client.read_holding_registers(address, **kw)
        except TypeError:
            continue
    return await client.read_holding_registers(address, count)


def u16s(v): return (v - 65536 if v > 32767 else v) / 10
def u16s100(v): return (v - 65536 if v > 32767 else v) / 100
def r32(regs, hi): return (regs[hi] << 16) | regs[hi + 1]
def valid(v): return v != 32766 and v != 65534


async def main():
    client = AsyncModbusTcpClient(host=HOST, port=PORT, timeout=10)
    await client.connect()
    print("Verbunden. Teste Block-Größen...\n")

    # Teste maximale Registerzahl pro Request
    print("=== Max. Register pro Request ===")
    for count in [1, 10, 20, 30, 40, 50, 60, 62, 63, 64, 80, 88, 100, 125]:
        r = await rhr(client, 690, count)
        ok = "OK" if not r.isError() else f"FEHLER (exc={getattr(r, 'exception_code', '?')})"
        print(f"  {count:3d} Register ab 690: {ok}")
        if not r.isError():
            break

    # Block 2 in 10er Schritten
    print("\n=== Block 2: 40690-40751 in 10er-Chunks ===")
    for start in range(690, 752, 10):
        count = min(10, 752 - start)
        r = await rhr(client, start, count)
        if r.isError():
            print(f"  40{start}: FEHLER (exc={getattr(r, 'exception_code', '?')})")
        else:
            vals = [r.registers[i] for i in range(count)]
            print(f"  40{start}: {vals}")

    # Block 3 in 10er Schritten
    print("\n=== Block 3: 40012-40099 in 10er-Chunks ===")
    for start in range(12, 100, 10):
        count = min(10, 100 - start)
        r = await rhr(client, start, count)
        if r.isError():
            print(f"  40{start:03d}: FEHLER (exc={getattr(r, 'exception_code', '?')})")
        else:
            vals = [r.registers[i] for i in range(count)]
            print(f"  40{start:03d}: {vals}")

    # Einzelne wichtige Register prüfen
    print("\n=== Einzelregister-Check ===")
    for addr, label in [
        (690, "T9 Speicher1 oben"),
        (691, "T10 Speicher1 unten"),
        (692, "Soll VL Boiler1"),
        (693, "Status Boiler1"),
        (694, "Pumpe Boiler1"),
        (706, "Drehzahl Puffer"),
        (709, "Ventilstellung"),
        (711, "Software Version"),
        (730, "Wärmemenge Hi"),
        (731, "Wärmemenge Lo"),
        (734, "Leistung Hi"),
        (735, "Leistung Lo"),
        (740, "Durchfluss Hi"),
        (741, "Durchfluss Lo"),
        (746, "RL Temp Zähler"),
        (747, "VL Temp Zähler"),
        (749, "Betriebstage"),
        (12,  "Offset Außentemp"),
        (23,  "Volle Nachtabs."),
        (80,  "Boilersoll1"),
    ]:
        r = await rhr(client, addr, 1)
        if r.isError():
            print(f"  {addr+40000} ({label}): FEHLER")
        else:
            v = r.registers[0]
            print(f"  {addr+40000} ({label}): {v}  (= {u16s(v):.1f} als x.x°C)")

    print("\nFertig.")
    client.close()


asyncio.run(main())
