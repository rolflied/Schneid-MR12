# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Home Assistant Custom Integration for the **Schneid MR-12** Fernwärme-Übergabestation (district heating transfer station) via Modbus TCP.

Integration domain: `schneid_mr12`
Integration path: `custom_components/schneid_mr12/`
Device: `192.168.5.214:2001`, Slave ID 1

## Development Commands

There is no build/test framework. Development workflow:

```bash
# Test Modbus connectivity and live register values
python modbus_test.py

# Probe register block boundaries and detect sentinel values
python modbus_probe.py

# Generate Excel register map from device docs
python generate_excel.py
```

To deploy: copy `custom_components/schneid_mr12/` into the Home Assistant `config/custom_components/` directory and restart HA.

## Architecture

### Data Flow

```
ConfigEntry (host, port, slave_id, scan_interval, circuits, read_only)
  → SchneidModbusCoordinator  (coordinator.py)
    → AsyncModbusTcpClient    (pymodbus, version-agnostic via _rhr())
      → 7 register blocks     → coordinator.data dict
        → Sensor / BinarySensor / Number / Select platforms
```

### Key Files

| File | Role |
|------|------|
| `const.py` | All register addresses, sentinel values, status enums, operating mode maps |
| `coordinator.py` | `DataUpdateCoordinator`; reads all register blocks; `_rhr()` + `async_write_register()` handle pymodbus version compat |
| `entity.py` | `SchneidBaseEntity` base class; device info for 5 sub-devices (Main, FW, HK0-3, Puffer) |
| `config_flow.py` | ConfigFlow + OptionsFlow: host/port/slave/interval/circuits/read-only |
| `sensor.py` / `binary_sensor.py` / `number.py` / `select.py` | Platform entity definitions |

### Register Blocks (coordinator.py `_read_all`)

| Block | Addresses | Content |
|-------|-----------|---------|
| 1a | 40600–40629 | Main temps, HK0/HK1 |
| 1b | 40630–40648 | HK2/HK3 |
| 2  | 40690–40729 | Boiler, pumps, diagnostics |
| 3b | 40730–40735 | Internal heat meter (kWh, volume, power) — uint32, 2 regs each |
| 3c | 40117–40121 | HK1 heating curve setpoints |
| 4  | 40012–40099 | System parameters |
| 5  | 40215–40244 | WÜST function, operating modes |

### Modbus Conventions

- **TCP only** (no RTU)
- **Address offset:** `pymodbus_address = PDF_register − 40000`
  e.g. PDF register 40600 → pymodbus address 600
- **Temperature scaling:** x.x°C → raw/10 (signed 16-bit); x.xx°C → raw/100
- **32-bit values:** High-Word first (big-endian word order)
- **Sentinel values:** `0x7FFE` = 32766 (temp not configured), `0xFFFE` = 65534 (status), `0x7E` = 126 (speed) — treat as unavailable

### pymodbus Compatibility

`_rhr()` and `async_write_register()` try keyword args sequentially:
`device_id=` (3.8+) → `slave=` (3.0–3.7) → `unit=` (2.x) → positional (fallback)

### Device Specifics (live findings)

- Only **HK1** is active; HK0, HK2, HK3 return sentinel values
- Internal heat meter (40730–40735) is available: heat energy, volume, power
- External counter registers (42731+) return exception code 2 (illegal address)
- Boiler registers (40080–40084) all return sentinel (no boiler installed)
- Date register order: 40717=day, 40718=month, 40719=weekday, 40720=year (year offset: 26 = 2026)

### Entity Design Patterns

- **Dynamic entity creation:** entities for HK0–3 are only created for circuits selected in ConfigFlow
- **Read-only mode:** disables all `Number` and `Select` entities when enabled
- **Energy Dashboard:** `waermemenge_fw` uses `device_class=GAS` (kWh, `TOTAL_INCREASING`) to appear under gas consumption
- **Sub-devices:** FW, each HKx, and Puffer appear as separate HA devices linked to the main MR-12 device

### HA Package (`ha_package_fernwaerme.yaml`)

Separate HA package (not part of the integration) providing:
- `input_number` for energy price
- `utility_meter` for consumption tracking
- Template sensors for cost calculations
