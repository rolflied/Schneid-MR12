# Schneid MR-12 – Home Assistant Integration

![Schneid MR-12](custom_components/schneid_mr12/brand/logo@2x.png)

Custom integration for the **Schneid MR-12 district heating transfer station** via Modbus TCP.

This integration reads temperatures, operating states, pumps, and the internal heat meter of the MR-12 and exposes them as Home Assistant entities. Writable parameters (setpoints, operating modes) can optionally be enabled.

> **Disclaimer:** This is **not** an official integration by Schneid or Home Assistant. It is an independent, community-driven project with no affiliation to Schneid GmbH.

> **Note:** This integration is in an early development stage and has been tailored to the needs of my own system. It is possible that other MR-12 installations use different Modbus registers or that parameters relevant to certain system configurations are missing. I welcome feedback, bug reports, and improvement suggestions – please open an [Issue](../../issues) or [Pull Request](../../pulls).

---

## Prerequisites

- Home Assistant 2024.1 or newer
- Schneid MR-12 with Modbus TCP interface enabled
- Network access from Home Assistant to the transfer station (default port: 2001)
- `pymodbus` ≥ 3.5.0, < 4.0.0 (managed automatically by HA)

---

## Installation

### Manual

1. Copy the `custom_components/schneid_mr12/` folder into the `config/custom_components/` directory of your Home Assistant installation.
2. Restart Home Assistant.

### HACS (not officially listed)

1. HACS → Integrations → ⋮ → Custom Repositories
2. Enter the URL of this repository, category: **Integration**
3. Install the integration and restart Home Assistant.

---

## Setup

1. **Settings → Devices & Services → Add Integration**
2. Search for "Schneid MR-12" and select it.
3. Enter the connection details:

| Field | Description | Default |
|-------|-------------|---------|
| Host | IP address of the transfer station | – |
| Port | Modbus TCP port | `2001` |
| Slave ID | Modbus slave ID | `1` |
| Scan interval | Seconds between updates | `30` |
| Heating circuits | Active heating circuits (HC0–HC3) | HC1 |
| Read-only | Disable write access | no |

The connection is automatically verified when saving.

---

## Entities

The integration creates multiple sub-devices:

### Main Device
| Entity | Description |
|--------|-------------|
| Outdoor temperature | Current outdoor temperature |
| Outdoor temperature average | Short-term average |
| Outdoor temperature average long-term | Long-term average |
| Software version | Diagnostics |

### District Heating
| Entity | Description |
|--------|-------------|
| Supply temperature actual | Secondary supply |
| Supply temperature setpoint | Calculated setpoint |
| Return temperature actual | Secondary return |
| Return temperature primary | Primary-side return |
| Valve position | Opening degree of the control valve (%) |
| Status | Operating state of the transfer station |
| Heat amount | Total heat energy (kWh) |
| Power | Current heat output (W) |
| Volume | Total flow volume (l) |

### Heating Circuit (per active circuit)
| Entity | Description |
|--------|-------------|
| Supply temperature actual / setpoint | Heating circuit supply temperature |
| Status | Operating state of the heating circuit |
| Mixer position | Position of the mixer |
| Operating mode | Configurable: Auto / Day / Night / Standby |
| Heating curve setpoints | Configurable: supply temperatures at +20/+5/−10 °C outdoor, Min/Max |

### Buffer Storage
| Entity | Description |
|--------|-------------|
| Temperature top / bottom | Storage sensors |
| Buffer pump speed | Current pump speed (%) |
| Switch-on / switch-off temperature | Configurable |

### Binary Sensors
Pumps (heating circuit, buffer, solar) and error messages as `binary_sensor`.

---

## Energy Dashboard

The **Heat amount** sensor (`sensor.schneid_mr12_waermemenge`) can be added to the Home Assistant Energy Dashboard under **Gas consumption**. The sensor uses `device_class: gas` with the unit `kWh` and is therefore directly compatible.

---

## Read-Only Mode

When **Read-only** is enabled, all `number` and `select` entities are disabled. Sensor readings remain available. This option is recommended when the MR-12 is primarily managed by a heating technician.

---

## Supported Devices

Tested with:
- **Schneid MR-12** district heating transfer station

---

## License

MIT License
