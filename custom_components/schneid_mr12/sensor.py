"""Sensor-Entitäten für Schneid MR-12."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_HEATING_CIRCUITS,
    DEFAULT_HEATING_CIRCUITS,
    DOMAIN,
    STATUS_BOILERKREIS,
    STATUS_HEIZKREIS,
    STATUS_MISCHER,
    STATUS_UEBERGABE,
)
from .coordinator import SchneidModbusCoordinator
from .entity import (
    SchneidBaseEntity,
    device_info_fw,
    device_info_hk,
    device_info_main,
    device_info_puffer,
)


@dataclass(frozen=True)
class SchneidSensorDescription(SensorEntityDescription):
    """Erweiterte Sensor-Beschreibung."""

    data_key: str = ""
    enum_map: dict[int, str] | None = None
    entity_category: EntityCategory | None = None


# ─── Haupt-/Stations-Sensoren ─────────────────────────────────────────────────

SENSOR_DESC_MAIN: tuple[SchneidSensorDescription, ...] = (
    SchneidSensorDescription(
        key="t6_aussentemperatur",
        data_key="t6_aussentemperatur",
        name="Außentemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer",
    ),
    SchneidSensorDescription(
        key="aussentemp_mittel",
        data_key="aussentemp_mittel",
        name="Außentemperatur Mittel",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer",
    ),
    SchneidSensorDescription(
        key="aussentemp_mittel_lz",
        data_key="aussentemp_mittel_lz",
        name="Außentemperatur Mittel Langzeit",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-low",
    ),
    SchneidSensorDescription(
        key="software_version",
        data_key="software_version",
        name="Softwareversion",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SchneidSensorDescription(
        key="hydraulikvariante",
        data_key="hydraulikvariante",
        name="Hydraulikvariante",
        icon="mdi:pipe",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SchneidSensorDescription(
        key="reset_counter",
        data_key="reset_counter",
        name="Reset-Zähler",
        icon="mdi:restart",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SchneidSensorDescription(
        key="regler_zeit",
        data_key="regler_zeit",
        name="Regler-Uhrzeit",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

# ─── Fernwärme-Sensoren ───────────────────────────────────────────────────────

SENSOR_DESC_FW: tuple[SchneidSensorDescription, ...] = (
    SchneidSensorDescription(
        key="t8_vl_sekundaer",
        data_key="t8_vl_sekundaer",
        name="Vorlauf Ist",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-water",
    ),
    SchneidSensorDescription(
        key="t11_rl_sekundaer",
        data_key="t11_rl_sekundaer",
        name="Rücklauf Ist",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-water",
    ),
    SchneidSensorDescription(
        key="vl_soll_sekundaer",
        data_key="vl_soll_sekundaer",
        name="Vorlauf Soll",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-lines",
    ),
    SchneidSensorDescription(
        key="t7_rl_primaer",
        data_key="t7_rl_primaer",
        name="Rücklauf Primär Ist",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-water",
    ),
    SchneidSensorDescription(
        key="max_rl_primaer",
        data_key="max_rl_primaer",
        name="Rücklauf Primär Max",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-alert",
    ),
    SchneidSensorDescription(
        key="status_uebergabe",
        data_key="status_uebergabe",
        name="Status",
        icon="mdi:transfer-station",
        enum_map=STATUS_UEBERGABE,
    ),
    SchneidSensorDescription(
        key="ventilstellung",
        data_key="ventilstellung",
        name="Ventilstellung",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:valve",
    ),
    SchneidSensorDescription(
        key="waermemenge_fw",
        data_key="waermemenge_fw",
        name="Wärmemenge",
        # device_class=GAS + kWh ermöglicht Einbindung im Energie-Dashboard
        # unter "Gasverbrauch" als kWh-basierter Zähler
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        icon="mdi:counter",
        # Interner Wärmezähler liefert ohne angeschlossenen Zähler dauerhaft 0
        entity_registry_enabled_default=False,
    ),
    SchneidSensorDescription(
        key="leistung_fw",
        data_key="leistung_fw",
        name="Leistung",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
        # Interner Wärmezähler liefert ohne angeschlossenen Zähler dauerhaft 0
        entity_registry_enabled_default=False,
    ),
    SchneidSensorDescription(
        key="volumen_fw",
        data_key="volumen_fw",
        name="Volumen",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
        icon="mdi:water-outline",
        # Interner Wärmezähler liefert ohne angeschlossenen Zähler dauerhaft 0
        entity_registry_enabled_default=False,
    ),
)

# ─── Pufferspeicher-Sensoren ──────────────────────────────────────────────────

SENSOR_DESC_PUFFER: tuple[SchneidSensorDescription, ...] = (
    SchneidSensorDescription(
        key="t9_speicher1_oben",
        data_key="t9_speicher1_oben",
        name="Temperatur Oben",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:water-boiler",
    ),
    SchneidSensorDescription(
        key="t10_speicher1_unten",
        data_key="t10_speicher1_unten",
        name="Temperatur Unten",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:water-boiler",
    ),
    SchneidSensorDescription(
        key="soll_vl_boiler1",
        data_key="soll_vl_boiler1",
        name="Vorlauf Soll Boiler 1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:water-boiler-alert",
    ),
    SchneidSensorDescription(
        key="status_boiler1",
        data_key="status_boiler1",
        name="Status Boiler 1",
        icon="mdi:water-boiler",
        enum_map=STATUS_BOILERKREIS,
    ),
    SchneidSensorDescription(
        key="einschalt_puffer",
        data_key="einschalt_puffer",
        name="Pumpeinschalttemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-plus",
    ),
    SchneidSensorDescription(
        key="ausschalt_puffer",
        data_key="ausschalt_puffer",
        name="Pumpausschalttemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:thermometer-minus",
    ),
    SchneidSensorDescription(
        key="drehzahl_puffer",
        data_key="drehzahl_puffer",
        name="Pufferpumpe Drehzahl",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    SchneidSensorDescription(
        key="drehzahl_solar",
        data_key="drehzahl_solar",
        name="Solarpumpe Drehzahl",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
    ),
)


# ─── Heizkreis-Sensoren (pro Kreis) ──────────────────────────────────────────

def _hk_sensors(hk_idx: int) -> tuple[SchneidSensorDescription, ...]:
    """Erzeugt Sensor-Beschreibungen für einen Heizkreis."""
    n = hk_idx
    return (
        SchneidSensorDescription(
            key=f"vl_hk{n}",
            data_key=f"vl_hk{n}",
            name="Vorlauf Ist",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=1,
            icon="mdi:radiator",
        ),
        SchneidSensorDescription(
            key=f"soll_hk{n}",
            data_key=f"soll_hk{n}",
            name="Vorlauf Soll",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=1,
            icon="mdi:radiator",
        ),
        SchneidSensorDescription(
            key=f"status_hk{n}",
            data_key=f"status_hk{n}",
            name="Status",
            icon="mdi:heat-wave",
            enum_map=STATUS_HEIZKREIS,
        ),
        SchneidSensorDescription(
            key=f"mischer_hk{n}",
            data_key=f"mischer_hk{n}",
            name="Mischer Stellung",
            icon="mdi:valve-open",
            enum_map=STATUS_MISCHER,
        ),
    )


# ─── Dynamische Icons ─────────────────────────────────────────────────────────

_STATUS_UEBERGABE_ICONS: dict[int, str] = {
    0: "mdi:power-off",
    1: "mdi:transfer-station",
    2: "mdi:thermometer-alert",
    3: "mdi:gauge-low",
    4: "mdi:hand-back-right",
}


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

    entities: list[SensorEntity] = []

    # Haupt-Gerät
    di_main = device_info_main(eid)
    for desc in SENSOR_DESC_MAIN:
        entities.append(SchneidSensor(coordinator, eid, desc, di_main))

    # Fernwärme-Gerät
    di_fw = device_info_fw(eid)
    for desc in SENSOR_DESC_FW:
        entities.append(SchneidSensor(coordinator, eid, desc, di_fw))

    # Pufferspeicher-Gerät
    di_puffer = device_info_puffer(eid)
    for desc in SENSOR_DESC_PUFFER:
        entities.append(SchneidSensor(coordinator, eid, desc, di_puffer))

    # Heizkreis-Geräte (nur aktivierte)
    for hk_idx in range(4):
        if hk_idx not in enabled_hks:
            continue
        di_hk = device_info_hk(eid, hk_idx)
        for desc in _hk_sensors(hk_idx):
            entities.append(SchneidSensor(coordinator, eid, desc, di_hk))

    async_add_entities(entities)


# ─── Sensor-Klasse ───────────────────────────────────────────────────────────

class SchneidSensor(SchneidBaseEntity, SensorEntity):
    """Eine Sensor-Entität des Schneid MR-12."""

    entity_description: SchneidSensorDescription

    def __init__(
        self,
        coordinator: SchneidModbusCoordinator,
        entry_id: str,
        description: SchneidSensorDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator, entry_id, description.key, device_info)
        self.entity_description = description
        if description.entity_category is not None:
            self._attr_entity_category = description.entity_category

    @property
    def native_value(self) -> Any:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        if raw is None:
            return None
        if self.entity_description.enum_map is not None:
            return self.entity_description.enum_map.get(int(raw), str(raw))
        return raw

    @property
    def icon(self) -> str | None:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        key = self.entity_description.key

        if key == "status_uebergabe" and raw is not None:
            return _STATUS_UEBERGABE_ICONS.get(int(raw), "mdi:transfer-station")

        if key == "ventilstellung" and raw is not None:
            return "mdi:valve-open" if int(raw) > 10 else "mdi:valve-closed"

        return self.entity_description.icon
