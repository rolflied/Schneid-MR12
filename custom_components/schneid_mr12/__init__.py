"""Schneid MR-12 Fernwärme-Integration für Home Assistant."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from modbus_connection import ModbusTcpParams

from homeassistant.components.modbus import async_get_unit
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import CONF_SCAN_INTERVAL, CONF_SLAVE_ID, DEFAULT_SCAN_INTERVAL
from .coordinator import SchneidConfigEntry, SchneidModbusCoordinator
from .entity import device_info_main

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
]


def create_modbus_params(config: Mapping[str, Any]) -> ModbusTcpParams:
    """Baut die Verbindungsparameter aus der Konfiguration."""
    return ModbusTcpParams(host=config[CONF_HOST], port=config[CONF_PORT])


async def async_setup_entry(hass: HomeAssistant, entry: SchneidConfigEntry) -> bool:
    """Richtet einen Config-Entry ein."""
    # Optionen überschreiben ursprüngliche Daten (falls Options-Flow verwendet wurde)
    config = {**entry.data, **entry.options}

    # Geteilte Verbindung aus der HA-Modbus-Integration; wird beim Entladen des
    # Entries automatisch freigegeben.
    unit = async_get_unit(
        hass, entry, create_modbus_params(config), config[CONF_SLAVE_ID]
    )
    coordinator = SchneidModbusCoordinator(
        hass,
        entry,
        unit,
        scan_interval=config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    # Hauptgerät vorab registrieren: Die Untergeräte (Fernwärme, Puffer,
    # Heizkreise) verweisen per via_device_id auf seine Geräte-ID.
    main_device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, **device_info_main(entry.entry_id)
    )
    coordinator.main_device_id = main_device.id
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SchneidConfigEntry) -> bool:
    """Entfernt einen Config-Entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: SchneidConfigEntry) -> None:
    """Wird aufgerufen, wenn sich die Optionen geändert haben."""
    await hass.config_entries.async_reload(entry.entry_id)
