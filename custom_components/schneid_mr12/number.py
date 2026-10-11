"""Number-Entitäten (schreibbare Sollwerte) für Schneid MR-12."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_HEATING_CIRCUITS,
    CONF_READ_ONLY,
    DEFAULT_HEATING_CIRCUITS,
    DEFAULT_READ_ONLY,
    DOMAIN,
)
from .coordinator import SchneidModbusCoordinator
from .entity import SchneidBaseEntity, device_info_hk, device_info_puffer


@dataclass(frozen=True)
class SchneidNumberDescription(NumberEntityDescription):
    """Beschreibung für Number-Entitäten."""

    data_key: str = ""
    register: int = 0
    write_scale: int = 1
    # "puffer" → Pufferspeicher-Gerät, "hk1" → Heizkreis 1
    device_group: str = "puffer"


NUMBER_DESCRIPTIONS_PUFFER: tuple[SchneidNumberDescription, ...] = (

    # ── Pufferspeicher – Schalttemperaturen ───────────────────────────────────
    SchneidNumberDescription(
        key="einschalt_puffer",
        data_key="einschalt_puffer",
        name="Puffer Einschalttemperatur",
        register=40704,
        native_min_value=20,
        native_max_value=80,
        native_step=0.1,
        # Register wird in 0,1 °C geführt (Lesen ÷10), also ×10 schreiben.
        write_scale=10,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-plus",
        mode=NumberMode.BOX,
        device_group="puffer",
    ),
    SchneidNumberDescription(
        key="ausschalt_puffer",
        data_key="ausschalt_puffer",
        name="Puffer Ausschalttemperatur",
        register=40705,
        native_min_value=20,
        native_max_value=80,
        native_step=0.1,
        # Register wird in 0,1 °C geführt (Lesen ÷10), also ×10 schreiben.
        write_scale=10,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-minus",
        mode=NumberMode.BOX,
        device_group="puffer",
    ),
)

NUMBER_DESCRIPTIONS_HK1: tuple[SchneidNumberDescription, ...] = (

    # ── Heizkreis 1 – Heizkurven-Sollwerte ───────────────────────────────────
    SchneidNumberDescription(
        key="hk1_vl_soll_20at",
        data_key="hk1_vl_soll_20at",
        name="VL-Soll bei +20°C AT",
        register=40117,
        native_min_value=10,
        native_max_value=70,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        mode=NumberMode.BOX,
        device_group="hk1",
    ),
    SchneidNumberDescription(
        key="hk1_vl_soll_5at",
        data_key="hk1_vl_soll_5at",
        name="VL-Soll bei +5°C AT",
        register=40118,
        native_min_value=10,
        native_max_value=70,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        device_group="hk1",
    ),
    SchneidNumberDescription(
        key="hk1_vl_soll_m10at",
        data_key="hk1_vl_soll_m10at",
        name="VL-Soll bei -10°C AT",
        register=40119,
        native_min_value=10,
        native_max_value=70,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-down",
        mode=NumberMode.BOX,
        device_group="hk1",
    ),
    SchneidNumberDescription(
        key="hk1_max_vl",
        data_key="hk1_max_vl",
        name="Max. Vorlauftemperatur",
        register=40120,
        native_min_value=20,
        native_max_value=80,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-plus",
        mode=NumberMode.BOX,
        device_group="hk1",
    ),
    SchneidNumberDescription(
        key="hk1_min_vl",
        data_key="hk1_min_vl",
        name="Min. Vorlauftemperatur",
        register=40121,
        native_min_value=10,
        native_max_value=60,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-minus",
        mode=NumberMode.BOX,
        device_group="hk1",
    ),
)


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

    entities: list[NumberEntity] = []
    for desc in NUMBER_DESCRIPTIONS_PUFFER:
        entities.append(SchneidNumber(coordinator, eid, desc, device_info_puffer(eid)))
    # Heizkurven-Sollwerte nur anlegen, wenn Heizkreis 1 auch aktiviert ist.
    if 1 in enabled_hks:
        for desc in NUMBER_DESCRIPTIONS_HK1:
            entities.append(SchneidNumber(coordinator, eid, desc, device_info_hk(eid, 1)))
    async_add_entities(entities)


class SchneidNumber(SchneidBaseEntity, NumberEntity):
    """Schreibbare Number-Entität des Schneid MR-12."""

    entity_description: SchneidNumberDescription

    def __init__(
        self,
        coordinator: SchneidModbusCoordinator,
        entry_id: str,
        description: SchneidNumberDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator, entry_id, description.key, device_info)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        if raw is None:
            return None
        return float(raw)

    async def async_set_native_value(self, value: float) -> None:
        scale = self.entity_description.write_scale
        raw_value = int(round(value * scale))
        if raw_value < 0:
            raw_value = raw_value & 0xFFFF

        # Wirft HomeAssistantError, wenn das Gerät den Schreibvorgang ablehnt.
        await self.coordinator.async_write_register(
            self.entity_description.register, raw_value
        )
        # Kein optimistisches Setzen des Caches: erst nach einer echten Rücklesung
        # den Wert übernehmen, damit die Oberfläche den tatsächlichen Gerätewert
        # zeigt und keinen Erfolg vortäuscht, der vom Gerät nicht übernommen wurde.
        await self.coordinator.async_request_refresh()
