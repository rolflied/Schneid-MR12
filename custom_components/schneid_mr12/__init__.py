"""Schneid MR-12 Fernwärme-Integration für Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_SCAN_INTERVAL, CONF_SLAVE_ID, DOMAIN
from .coordinator import SchneidModbusCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richtet einen Config-Entry ein."""
    # Optionen überschreiben ursprüngliche Daten (falls Options-Flow verwendet wurde)
    config = {**entry.data, **entry.options}

    coordinator = SchneidModbusCoordinator(
        hass=hass,
        host=config[CONF_HOST],
        port=config[CONF_PORT],
        slave_id=config[CONF_SLAVE_ID],
        scan_interval=config.get(CONF_SCAN_INTERVAL, 30),
    )

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady("Erster Datenempfang von MR-12 fehlgeschlagen")

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entfernt einen Config-Entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: SchneidModbusCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        if coordinator._client is not None:
            coordinator._client.close()
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Wird aufgerufen, wenn sich die Optionen geändert haben."""
    await hass.config_entries.async_reload(entry.entry_id)
