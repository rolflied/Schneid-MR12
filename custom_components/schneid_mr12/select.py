"""Select-Entitäten (schreibbare Auswahlfelder) für Schneid MR-12."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_READ_ONLY,
    DEFAULT_READ_ONLY,
    DOMAIN,
    FUNKTION_WUEST_OPTIONS,
)
from .coordinator import SchneidModbusCoordinator
from .entity import SchneidBaseEntity, device_info_main


@dataclass(frozen=True)
class SchneidSelectDescription(SelectEntityDescription):
    """Beschreibung für Select-Entitäten."""

    data_key: str = ""
    register: int = 0
    options_map: dict[int, str] | None = None


def _invert(m: dict[int, str]) -> dict[str, int]:
    return {v: k for k, v in m.items()}


# ─── Stations-Selects (Hauptgerät) ───────────────────────────────────────────

SELECT_DESC_MAIN: tuple[SchneidSelectDescription, ...] = (
    SchneidSelectDescription(
        key="funktion_wuest",
        data_key="funktion_wuest",
        name="Betriebsmodus",
        register=40215,
        options_map=FUNKTION_WUEST_OPTIONS,
        icon="mdi:tune",
    ),
)


# ─── Platform-Setup ──────────────────────────────────────────────────────────

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    config = {**entry.data, **entry.options}
    if config.get(CONF_READ_ONLY, DEFAULT_READ_ONLY):
        return  # Im Nur-Lese-Modus keine schreibbaren Entitäten anlegen

    coordinator: SchneidModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    eid = entry.entry_id

    async_add_entities(
        SchneidSelect(coordinator, eid, desc, device_info_main(eid))
        for desc in SELECT_DESC_MAIN
    )


class SchneidSelect(SchneidBaseEntity, SelectEntity):
    """Schreibbare Select-Entität des Schneid MR-12."""

    entity_description: SchneidSelectDescription

    def __init__(
        self,
        coordinator: SchneidModbusCoordinator,
        entry_id: str,
        description: SchneidSelectDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator, entry_id, description.key, device_info)
        self.entity_description = description
        if description.options_map:
            self._attr_options = list(description.options_map.values())

    @property
    def current_option(self) -> str | None:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        if raw is None:
            return None
        omap = self.entity_description.options_map
        if omap:
            return omap.get(int(raw))
        return str(raw)

    @property
    def icon(self) -> str | None:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        key = self.entity_description.key

        if key == "funktion_wuest" and raw is not None:
            v = int(raw)
            if v == 0:
                return "mdi:power-off"
            if v == 5:
                return "mdi:party-popper"
            if v == 6:
                return "mdi:wrench"

        return self.entity_description.icon

    async def async_select_option(self, option: str) -> None:
        omap = self.entity_description.options_map
        if omap is None:
            return
        value = _invert(omap).get(option)
        if value is None:
            return

        # Wirft HomeAssistantError, wenn das Gerät den Schreibvorgang ablehnt.
        await self.coordinator.async_write_register(
            self.entity_description.register, value
        )
        # Kein optimistisches Setzen des Caches: echter Gerätewert per Rücklesung.
        await self.coordinator.async_request_refresh()
