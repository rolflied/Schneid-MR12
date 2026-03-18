"""Config Flow für Schneid MR-12."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import AsyncModbusTcpClient

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    BooleanSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

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


async def _test_connection(host: str, port: int) -> bool:
    """Versucht, eine Verbindung zum Gerät herzustellen."""
    client = AsyncModbusTcpClient(host=host, port=port, timeout=5)
    try:
        return await client.connect()
    except Exception:
        return False
    finally:
        client.close()


class SchneidMR12ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Schneid MR-12."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            if not await _test_connection(host, port):
                errors["base"] = "cannot_connect"
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
    ) -> FlowResult:
        errors: dict[str, str] = {}

        current = {**self.config_entry.data, **self.config_entry.options}

        if user_input is not None:
            host = user_input.get(CONF_HOST, current[CONF_HOST])
            port = user_input.get(CONF_PORT, current[CONF_PORT])

            if not await _test_connection(host, port):
                errors["base"] = "cannot_connect"
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
