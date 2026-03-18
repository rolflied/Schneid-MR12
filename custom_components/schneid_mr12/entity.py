"""Basis-Entity und Geräte-Info-Helfer für Schneid MR-12."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SchneidModbusCoordinator


def device_info_main(entry_id: str) -> DeviceInfo:
    """Hauptgerät: Schneid MR-12 Übergabestation."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name="Schneid MR-12",
        manufacturer="Dagobert Duck",
        model="MR-12",
    )


def device_info_fw(entry_id: str) -> DeviceInfo:
    """Sub-Gerät: Fernwärmekreislauf."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry_id}_fw")},
        name="Fernwärme",
        manufacturer="Dagobert Duck",
        model="MR-12",
        via_device=(DOMAIN, entry_id),
    )


def device_info_hk(entry_id: str, hk_idx: int) -> DeviceInfo:
    """Sub-Gerät: Heizkreis 0–3."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry_id}_hk{hk_idx}")},
        name=f"Heizkreis {hk_idx}",
        manufacturer="Dagobert Duck",
        model="MR-12",
        via_device=(DOMAIN, entry_id),
    )


def device_info_puffer(entry_id: str) -> DeviceInfo:
    """Sub-Gerät: Pufferspeicher."""
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry_id}_puffer")},
        name="Pufferspeicher",
        manufacturer="Dagobert Duck",
        model="MR-12",
        via_device=(DOMAIN, entry_id),
    )


class SchneidBaseEntity(CoordinatorEntity[SchneidModbusCoordinator]):
    """Gemeinsame Basisklasse für alle Schneid-MR-12-Entitäten."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SchneidModbusCoordinator,
        entry_id: str,
        unique_suffix: str,
        device_info: DeviceInfo | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_{unique_suffix}"
        self._attr_device_info = device_info or device_info_main(entry_id)
