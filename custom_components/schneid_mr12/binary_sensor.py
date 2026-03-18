"""Binäre Sensor-Entitäten für Schneid MR-12 (Pumpen, Fehler, Status)."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HEATING_CIRCUITS, DEFAULT_HEATING_CIRCUITS, DOMAIN
from .coordinator import SchneidModbusCoordinator
from .entity import (
    SchneidBaseEntity,
    device_info_fw,
    device_info_hk,
    device_info_puffer,
)


@dataclass(frozen=True)
class SchneidBinarySensorDescription(BinarySensorEntityDescription):
    """Beschreibung für binäre Sensoren."""

    data_key: str = ""
    on_value: int | None = None
    icon_on: str | None = None
    icon_off: str | None = None
    entity_category: EntityCategory | None = None


# ─── Fernwärme-Binärsensoren ─────────────────────────────────────────────────

BINARY_DESC_FW: tuple[SchneidBinarySensorDescription, ...] = (
    SchneidBinarySensorDescription(
        key="zubringpumpe",
        data_key="zubringpumpe",
        name="Zubringpumpe",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_on="mdi:pump",
        icon_off="mdi:pump-off",
    ),
    SchneidBinarySensorDescription(
        key="leistungsbegrenzung_aktiv",
        data_key="leistungsbegrenzung",
        name="Leistungsbegrenzung aktiv",
        device_class=BinarySensorDeviceClass.POWER,
        on_value=1,
        icon_on="mdi:gauge-low",
        icon_off="mdi:gauge",
    ),
)

# ─── Pufferspeicher-Binärsensoren ────────────────────────────────────────────

BINARY_DESC_PUFFER: tuple[SchneidBinarySensorDescription, ...] = (
    SchneidBinarySensorDescription(
        key="pumpe_boiler1",
        data_key="pumpe_boiler1",
        name="Pumpe Boiler 1",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_on="mdi:pump",
        icon_off="mdi:pump-off",
    ),
)


# ─── Heizkreis-Binärsensoren (pro Kreis) ─────────────────────────────────────

def _hk_binary(hk_idx: int) -> tuple[SchneidBinarySensorDescription, ...]:
    return (
        SchneidBinarySensorDescription(
            key=f"pumpe_hk{hk_idx}",
            data_key=f"pumpe_hk{hk_idx}",
            name="Pumpe",
            device_class=BinarySensorDeviceClass.RUNNING,
            icon_on="mdi:pump",
            icon_off="mdi:pump-off",
        ),
    )


# ─── Platform-Setup ──────────────────────────────────────────────────────────

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SchneidModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    config = {**entry.data, **entry.options}
    enabled_hks = {int(h) for h in config.get(CONF_HEATING_CIRCUITS, DEFAULT_HEATING_CIRCUITS)}
    eid = entry.entry_id

    entities: list[BinarySensorEntity] = []

    di_fw = device_info_fw(eid)
    for desc in BINARY_DESC_FW:
        entities.append(SchneidBinarySensor(coordinator, eid, desc, di_fw))

    di_puffer = device_info_puffer(eid)
    for desc in BINARY_DESC_PUFFER:
        entities.append(SchneidBinarySensor(coordinator, eid, desc, di_puffer))

    for hk_idx in range(4):
        if hk_idx not in enabled_hks:
            continue
        di_hk = device_info_hk(eid, hk_idx)
        for desc in _hk_binary(hk_idx):
            entities.append(SchneidBinarySensor(coordinator, eid, desc, di_hk))

    async_add_entities(entities)


class SchneidBinarySensor(SchneidBaseEntity, BinarySensorEntity):
    """Binäre Sensor-Entität des Schneid MR-12."""

    entity_description: SchneidBinarySensorDescription

    def __init__(
        self,
        coordinator: SchneidModbusCoordinator,
        entry_id: str,
        description: SchneidBinarySensorDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator, entry_id, description.key, device_info)
        self.entity_description = description
        if description.entity_category is not None:
            self._attr_entity_category = description.entity_category

    @property
    def is_on(self) -> bool | None:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        if raw is None:
            return None
        if self.entity_description.on_value is not None:
            return int(raw) == self.entity_description.on_value
        return int(raw) > 0

    @property
    def icon(self) -> str | None:
        if self.is_on:
            return self.entity_description.icon_on
        return self.entity_description.icon_off
