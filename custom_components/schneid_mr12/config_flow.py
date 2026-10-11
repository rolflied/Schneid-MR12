"""Config Flow für Schneid MR-12."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from modbus_connection import ModbusError

from homeassistant import config_entries
from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    BooleanSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from . import create_modbus_params
from .const import (
    CONF_HEATING_CIRCUITS,
    CONF_READ_ONLY,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_HEATING_CIRCUITS,
    DEFAULT_PORT,
    DEFAULT_READ_ONLY,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

_HK_SELECTOR = SelectSelector(
    SelectSelectorConfig(
        options=[
            {"value": "0", "label": "Heizkreis 0"},
            {"value": "1", "label": "Heizkreis 1"},
            {"value": "2", "label": "Heizkreis 2"},
            {"value": "3", "label": "Heizkreis 3"},
        ],
        multiple=True,
        mode=SelectSelectorMode.LIST,
    )
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            int, vol.Range(min=1, max=65535)
        ),
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
            int, vol.Range(min=1, max=247)
        ),
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=5, max=3600)
        ),
        vol.Required(
            CONF_HEATING_CIRCUITS, default=DEFAULT_HEATING_CIRCUITS
        ): _HK_SELECTOR,
        vol.Required(CONF_READ_ONLY, default=DEFAULT_READ_ONLY): BooleanSelector(),
    }
)


# Register, an dem der Verbindungstest prüft, ob wirklich ein MR-12 antwortet
# (40600, T6 Außentemperatur)
_PROBE_ADDRESS = 600


async def _test_connection(hass: HomeAssistant, config: dict[str, Any]) -> str | None:
    """Prüft, ob unter Host/Port/Slave-ID ein MR-12 per Modbus antwortet.

    Gibt ``None`` bei Erfolg zurück, sonst den Fehlerschlüssel für das Formular.
    """
    try:
        async with async_get_temporary_unit(
            hass, create_modbus_params(config), config[CONF_SLAVE_ID]
        ) as unit:
            await unit.read_holding_registers(_PROBE_ADDRESS, 1)
    except (HomeAssistantError, ModbusError):
        _LOGGER.debug("Verbindungstest fehlgeschlagen", exc_info=True)
        return "cannot_connect"
    except Exception:
        _LOGGER.exception("Unerwarteter Fehler beim Verbindungstest")
        return "unknown"
    return None


class SchneidMR12ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Schneid MR-12."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            if error := await _test_connection(self.hass, user_input):
                errors["base"] = error
            else:
                unique_id = f"{host}:{port}:{user_input[CONF_SLAVE_ID]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Schneid MR-12 ({host})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
            description_placeholders={
                "default_port": str(DEFAULT_PORT),
                "default_slave": str(DEFAULT_SLAVE_ID),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SchneidMR12OptionsFlow:
        return SchneidMR12OptionsFlow()


class SchneidMR12OptionsFlow(config_entries.OptionsFlow):
    """Options Flow – erlaubt nachträgliche Änderung der Konfiguration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        current = {**self.config_entry.data, **self.config_entry.options}

        if user_input is not None:
            if error := await _test_connection(self.hass, {**current, **user_input}):
                errors["base"] = error
            else:
                return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current.get(CONF_HOST, "")): str,
                vol.Required(
                    CONF_PORT,
                    default=current.get(CONF_PORT, DEFAULT_PORT),
                ): vol.All(int, vol.Range(min=1, max=65535)),
                vol.Required(
                    CONF_SLAVE_ID,
                    default=current.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID),
                ): vol.All(int, vol.Range(min=1, max=247)),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(int, vol.Range(min=5, max=3600)),
                vol.Required(
                    CONF_HEATING_CIRCUITS,
                    default=current.get(CONF_HEATING_CIRCUITS, DEFAULT_HEATING_CIRCUITS),
                ): _HK_SELECTOR,
                vol.Required(
                    CONF_READ_ONLY,
                    default=current.get(CONF_READ_ONLY, DEFAULT_READ_ONLY),
                ): BooleanSelector(),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
