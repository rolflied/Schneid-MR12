"""Select-Entitäten (schreibbare Auswahlfelder) für Schneid MR-12."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    AUSHEIZPROGRAMM_OPTIONS,
    BETRIEBSMODUS_HK_OPTIONS,
    CONF_HEATING_CIRCUITS,
    CONF_READ_ONLY,
    DEFAULT_HEATING_CIRCUITS,
    DEFAULT_READ_ONLY,
    DOMAIN,
    FUNKTION_WUEST_OPTIONS,
    HANDBETRIEB_VENTIL_OPTIONS,
)
from .coordinator import SchneidModbusCoordinator
from .entity import SchneidBaseEntity, device_info_fw, device_info_hk, device_info_main


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
    SchneidSelectDescription(
        key="ausheizprogramm",
        data_key="ausheizprogramm",
        name="Ausheizprogramm",
        register=40030,
        options_map=AUSHEIZPROGRAMM_OPTIONS,
        icon="mdi:fire",
    ),
)

# ─── Fernwärme-Selects ────────────────────────────────────────────────────────

SELECT_DESC_FW: tuple[SchneidSelectDescription, ...] = (
    SchneidSelectDescription(
        key="handbetrieb_ventil",
        data_key="handbetrieb_ventil",
        name="Handbetrieb Primärventil",
        register=40050,
        options_map=HANDBETRIEB_VENTIL_OPTIONS,
        icon="mdi:valve",
    ),
)


# ─── Heizkreis-Selects (pro Kreis) ───────────────────────────────────────────

def _hk_selects(hk_idx: int) -> tuple[SchneidSelectDescription, ...]:
    return (
        SchneidSelectDescription(
            key=f"betriebsmodus_hk{hk_idx}",
            data_key=f"betriebsmodus_hk{hk_idx}",
            name="Betriebsmodus",
            register=40240 + hk_idx,
            options_map=BETRIEBSMODUS_HK_OPTIONS,
            icon="mdi:tune-variant",
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
    enabled_hks = {
        int(h) for h in config.get(CONF_HEATING_CIRCUITS, DEFAULT_HEATING_CIRCUITS)
    }

    entities: list[SchneidSelect] = []
    for desc in SELECT_DESC_MAIN:
        entities.append(SchneidSelect(coordinator, eid, desc, device_info_main(eid)))
    for desc in SELECT_DESC_FW:
        entities.append(SchneidSelect(coordinator, eid, desc, device_info_fw(eid)))
    for hk_idx in range(4):
        if hk_idx not in enabled_hks:
            continue
        di_hk = device_info_hk(eid, hk_idx)
        for desc in _hk_selects(hk_idx):
            entities.append(SchneidSelect(coordinator, eid, desc, di_hk))
    async_add_entities(entities)


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
