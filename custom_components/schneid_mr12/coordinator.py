"""DataUpdateCoordinator für Schneid MR-12 über Modbus TCP.

Die Verbindung kommt aus der Modbus-Integration von Home Assistant
(``homeassistant.components.modbus.async_get_unit``, seit HA 2026.9). Sie baut
die Verbindung bei Bedarf selbst auf, serialisiert alle Anfragen auf dem Gerät
und wird geteilt, falls weitere Integrationen dasselbe Gerät abfragen.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from modbus_connection import (
    IllegalFunctionError,
    ModbusError,
    ModbusExceptionError,
    ModbusTimeoutError,
    ModbusUnit,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Frühestens so lange nach einem Schreibvorgang wird geprüft, ob der Wert am
# Regler angekommen ist. Das CM12 schreibt zuerst in sein Spiegelregister und
# reicht die Änderung erst danach über RS485 an den Regler weiter; eine sofortige
# Rücklesung sieht deshalb nur den Spiegel.
WRITE_VERIFY_DELAY = 60  # Sekunden


@dataclass
class _PendingWrite:
    """Ein Schreibvorgang, dessen Übernahme noch geprüft werden muss."""

    pdf_register: int
    value: int
    written_at: float

# Sentinel-Werte des MR-12: zeigen an, dass ein Sensor/eine Funktion nicht verfügbar ist
_SENTINEL = frozenset({32766, 65534, 126})  # 0x7FFE, 0xFFFE, 0x007E
# Für Temperaturen gilt 126 (0x007E) NICHT als Sentinel: 126 entspricht 12,6 °C
# und ist ein völlig normaler Messwert. Das Gerät markiert fehlende Fühler mit
# 0x7FFE bzw. 0xFFFE; 0x007E tritt nur in Status-/Belegungsslots als „nicht
# vorhanden“ auf.
_SENTINEL_TEMP = frozenset({32766, 65534})  # 0x7FFE, 0xFFFE


def _u16_to_signed(value: int) -> int:
    """Wandelt einen vorzeichenlosen 16-Bit-Wert in einen vorzeichenbehafteten um."""
    if value > 32767:
        return value - 65536
    return value


def _read32(regs: list[int], hi_index: int) -> int:
    """Kombiniert zwei aufeinanderfolgende 16-Bit-Register zu einem vorzeichenlosen 32-Bit-Wert."""
    return (regs[hi_index] << 16) | regs[hi_index + 1]


def _read32s(regs: list[int], hi_index: int) -> int:
    """Kombiniert zwei aufeinanderfolgende 16-Bit-Register zu einem vorzeichenbehafteten 32-Bit-Wert."""
    v = (regs[hi_index] << 16) | regs[hi_index + 1]
    if v >= 0x80000000:
        v -= 0x100000000
    return v


def _temp(val: int) -> float | None:
    """Gibt x,x°C zurück oder None bei Sentinel."""
    if val in _SENTINEL_TEMP:
        return None
    return _u16_to_signed(val) / 10


def _temp100(val: int) -> float | None:
    """Gibt x,xx°C zurück oder None bei Sentinel."""
    if val in _SENTINEL_TEMP:
        return None
    return _u16_to_signed(val) / 100


def _status(val: int) -> int | None:
    """Gibt Statuswert zurück oder None bei Sentinel."""
    return None if val in _SENTINEL else val


def _regler_zeit(data: dict[str, Any]) -> datetime | None:
    """Baut aus Uhrzeit (hhmm), Tag, Monat und Jahr (zweistellig) einen Zeitstempel.

    Der Regler kennt keine Zeitzone; angenommen wird die Zeitzone von Home Assistant.
    """
    try:
        hhmm = data["uhrzeit"]
        jahr = data["jahr"]
        return datetime(
            jahr + 2000 if jahr < 100 else jahr,
            data["monat"],
            data["tag"],
            hhmm // 100,
            hhmm % 100,
            tzinfo=dt_util.get_default_time_zone(),
        )
    except (KeyError, ValueError):
        return None


type SchneidConfigEntry = ConfigEntry[SchneidModbusCoordinator]


class SchneidModbusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Koordinator für alle Modbus-Lese- und Schreibvorgänge."""

    config_entry: SchneidConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: SchneidConfigEntry,
        unit: ModbusUnit,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.unit = unit
        # Noch zu prüfende Schreibvorgänge, nach Modbus-Adresse
        self._pending_writes: dict[int, _PendingWrite] = {}

    async def _read_block(self, address: int, count: int) -> list[int] | None:
        """Liest einen Registerblock.

        Antwortet das Gerät mit einer Modbus-Exception (z. B. Register auf diesem
        Gerät nicht vorhanden), wird der Block übersprungen. Verbindungs- und
        Timeout-Fehler werden weitergereicht und lassen das ganze Update scheitern.
        """
        try:
            return await self.unit.read_holding_registers(address, count)
        except ModbusExceptionError as err:
            _LOGGER.debug("Block %s+%s übersprungen: %s", address, count, err)
            return None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self._read_all()
            await self._verify_pending_writes()
        except ModbusError as err:
            raise UpdateFailed(f"Modbus-Fehler: {err}") from err
        if not data:
            raise UpdateFailed("Das Gerät hat keinen der Registerblöcke beantwortet")
        return data

    async def _verify_pending_writes(self) -> None:
        """Prüft fällige Schreibvorgänge gegen den aktuellen Gerätewert.

        Läuft beim ersten Poll, der mindestens ``WRITE_VERIFY_DELAY`` Sekunden
        nach dem Schreiben stattfindet. Ein Lesefehler lässt den Eintrag für den
        nächsten Poll stehen.
        """
        now = time.monotonic()
        for address, pending in list(self._pending_writes.items()):
            if now - pending.written_at < WRITE_VERIFY_DELAY:
                continue
            if (regs := await self._read_block(address, 1)) is None:
                continue
            del self._pending_writes[address]
            actual = regs[0]
            if actual == pending.value:
                _LOGGER.info(
                    "Register %s: geschriebener Wert %s ist nach %.0f s weiterhin "
                    "gesetzt – vom Regler übernommen",
                    pending.pdf_register, pending.value, now - pending.written_at,
                )
            else:
                _LOGGER.warning(
                    "Register %s: geschrieben %s, nach %.0f s gelesen %s. Der Regler "
                    "hat den Wert nicht übernommen (oder er wurde inzwischen am "
                    "Gerät geändert). Das CM12 setzt direkte Modbus-Schreibvorgänge "
                    "auf dieses Register offenbar nicht um.",
                    pending.pdf_register, pending.value,
                    now - pending.written_at, actual,
                )

    async def _read_all(self) -> dict[str, Any]:
        """Liest alle benötigten Register-Blöcke und gibt ein Daten-Dict zurück."""
        data: dict[str, Any] = {}

        # ── Block 1a: Haupttemperaturen + Heizkreis 0 + 1 (40600-40629, 30 Reg.) ──
        if (regs := await self._read_block(600, 30)) is not None:
            if (v := _temp(regs[0])) is not None: data["t6_aussentemperatur"]  = v
            if (v := _temp(regs[1])) is not None: data["t7_rl_primaer"]        = v
            if (v := _temp(regs[2])) is not None: data["t8_vl_sekundaer"]      = v
            if (v := _temp(regs[3])) is not None: data["t11_rl_sekundaer"]     = v
            if (v := _temp(regs[4])) is not None: data["vl_soll_sekundaer"]    = v
            if (v := _temp(regs[5])) is not None: data["max_rl_primaer"]       = v
            if (v := _status(regs[6])) is not None: data["status_uebergabe"]   = v
            # Heizkreis 0 (Index 10..18 → Adressen 610..618)
            if (v := _temp(regs[10])) is not None: data["vl_hk0"]              = v
            if (v := _temp(regs[11])) is not None: data["soll_hk0"]            = v
            if (v := _temp(regs[12])) is not None: data["raumsoll_hk0"]        = v
            if (v := _temp(regs[13])) is not None: data["raumtemp_hk0"]        = v
            if (v := _status(regs[16])) is not None: data["pumpe_hk0"]         = v
            if (v := _status(regs[17])) is not None: data["status_hk0"]        = v
            if (v := _status(regs[18])) is not None: data["mischer_hk0"]       = v
            # Heizkreis 1 (Index 20..28 → Adressen 620..628)
            if (v := _temp(regs[20])) is not None: data["vl_hk1"]              = v
            if (v := _temp(regs[21])) is not None: data["soll_hk1"]            = v
            if (v := _temp(regs[22])) is not None: data["raumsoll_hk1"]        = v
            if (v := _temp(regs[23])) is not None: data["raumtemp_hk1"]        = v
            if (v := _status(regs[26])) is not None: data["pumpe_hk1"]         = v
            if (v := _status(regs[27])) is not None: data["status_hk1"]        = v
            if (v := _status(regs[28])) is not None: data["mischer_hk1"]       = v

        # ── Block 1b: Heizkreis 2 + 3 (40630-40648, 19 Reg.) ─────────────────
        if (regs := await self._read_block(630, 19)) is not None:
            # Heizkreis 2 (Index 0..8 → Adressen 630..638)
            if (v := _temp(regs[0])) is not None: data["vl_hk2"]               = v
            if (v := _temp(regs[1])) is not None: data["soll_hk2"]             = v
            if (v := _temp(regs[2])) is not None: data["raumsoll_hk2"]         = v
            if (v := _temp(regs[3])) is not None: data["raumtemp_hk2"]         = v
            if (v := _status(regs[6])) is not None: data["pumpe_hk2"]          = v
            if (v := _status(regs[7])) is not None: data["status_hk2"]         = v
            if (v := _status(regs[8])) is not None: data["mischer_hk2"]        = v
            # Heizkreis 3 (Index 10..18 → Adressen 640..648)
            if (v := _temp(regs[10])) is not None: data["vl_hk3"]              = v
            if (v := _temp(regs[11])) is not None: data["soll_hk3"]            = v
            if (v := _temp(regs[12])) is not None: data["raumsoll_hk3"]        = v
            if (v := _temp(regs[13])) is not None: data["raumtemp_hk3"]        = v
            if (v := _status(regs[16])) is not None: data["pumpe_hk3"]         = v
            if (v := _status(regs[17])) is not None: data["status_hk3"]        = v
            if (v := _status(regs[18])) is not None: data["mischer_hk3"]       = v

        # ── Block 2: Boiler + Pumpen + Diagnose (40690-40729, 40 Reg.) ────────
        # Der interne Wärmezähler (40730 ff.) wird separat in Block 3b gelesen.
        if (regs := await self._read_block(690, 40)) is not None:
            if (v := _temp(regs[0])) is not None: data["t9_speicher1_oben"]    = v
            if (v := _temp(regs[1])) is not None: data["t10_speicher1_unten"]  = v
            if (v := _temp(regs[2])) is not None: data["soll_vl_boiler1"]      = v
            if (v := _status(regs[3])) is not None: data["status_boiler1"]     = v
            if (v := _status(regs[4])) is not None: data["pumpe_boiler1"]      = v
            # regs[5-9]: Boiler 2 – nicht vorhanden auf diesem Gerät (Sentinel)
            if (v := _temp(regs[10])) is not None: data["vl_lademodul1"]       = v
            if (v := _temp(regs[11])) is not None: data["vl_lademodul2"]       = v
            if (v := _temp(regs[12])) is not None: data["temp_zirkulation1"]   = v
            if (v := _temp(regs[13])) is not None: data["temp_zirkulation2"]   = v
            if (v := _temp(regs[14])) is not None: data["einschalt_puffer"]    = v
            if (v := _temp(regs[15])) is not None: data["ausschalt_puffer"]    = v
            if regs[16] not in _SENTINEL: data["drehzahl_puffer"]              = regs[16]
            if regs[17] not in _SENTINEL: data["drehzahl_solar"]               = regs[17]
            if (v := _status(regs[18])) is not None: data["zubringpumpe"]      = v
            if regs[19] not in _SENTINEL: data["ventilstellung"]               = regs[19]
            if regs[20] not in _SENTINEL: data["status_sdcard"]                = regs[20]
            if regs[21] not in _SENTINEL: data["software_version"]             = regs[21]
            if regs[22] not in _SENTINEL: data["hydraulikvariante"]            = regs[22]
            # regs[24-25]: Zirkulationspumpen – nicht konfiguriert, Entitäten entfernt
            if regs[26] not in _SENTINEL: data["uhrzeit"]                      = regs[26]
            # Hinweis: Reihenfolge im Gerät ist Wochentag → Tag → Monat → Jahr
            if regs[27] not in _SENTINEL: data["wochentag"]                    = regs[27]  # 40717
            if regs[28] not in _SENTINEL: data["tag"]                          = regs[28]  # 40718
            if regs[29] not in _SENTINEL: data["monat"]                        = regs[29]  # 40719
            if regs[30] not in _SENTINEL: data["jahr"]                         = regs[30]  # 40720
            if (zeit := _regler_zeit(data)) is not None: data["regler_zeit"] = zeit
            if (v := _status(regs[31])) is not None: data["status_pumpe_lm1"] = v
            if (v := _status(regs[32])) is not None: data["status_mischer_lm1"] = v
            if (v := _status(regs[33])) is not None: data["status_pumpe_lm2"] = v
            if (v := _status(regs[34])) is not None: data["status_mischer_lm2"] = v
            if regs[36] not in _SENTINEL: data["reset_counter"]                = regs[36]
            if (v := _temp(regs[38])) is not None: data["aussentemp_mittel"]   = v   # 40728
            if (v := _temp(regs[39])) is not None: data["aussentemp_mittel_lz"] = v  # 40729

        # ── Block 3: Systemparameter + Boilersollwerte (40012-40099, 88 Reg.) ──
        if (regs := await self._read_block(12, 88)) is not None:
            # Index = Registeradresse - 12
            if regs[0] not in _SENTINEL: data["offset_aussentemp"]    = _u16_to_signed(regs[0]) / 10   # 40012
            if regs[11] not in _SENTINEL: data["volle_nachtabsenkung"] = _u16_to_signed(regs[11])        # 40023 (Außentemp, kann negativ sein)
            if regs[12] not in _SENTINEL: data["keine_nachtabsenkung"] = _u16_to_signed(regs[12])        # 40024 (Außentemp, kann negativ sein)
            if regs[16] not in _SENTINEL: data["vl_bei_frost"]         = regs[16]                       # 40028
            if regs[17] not in _SENTINEL: data["frost_aussentemp"]     = _u16_to_signed(regs[17])       # 40029
            if regs[18] not in _SENTINEL: data["ausheizprogramm"]      = regs[18]                       # 40030
            if regs[37] not in _SENTINEL: data["stationserhöhung"]     = regs[37]                       # 40049
            if regs[38] not in _SENTINEL: data["handbetrieb_ventil"]   = regs[38]                       # 40050
            if regs[41] not in _SENTINEL: data["leistungsbegrenzung"]  = regs[41]                       # 40053
            # regs[68-72]: Boilersollwerte 40080-40084 – alle Sentinel auf diesem Gerät

        # ── Block 3b: Interner Wärmezähler (40730-40735, 6 Reg.) ──────────────
        # 40730+40731: Wärmemenge  (uint32, 0,1 kWh → /10 → kWh)
        # 40732+40733: Volumen     (uint32, Einheit Liter)
        # 40734+40735: Leistung    (uint32, Einheit W)
        if (regs := await self._read_block(730, 6)) is not None:
            data["waermemenge_fw"] = _read32(regs, 0) / 10   # 40730+40731
            data["volumen_fw"]     = _read32(regs, 2)         # 40732+40733
            data["leistung_fw"]    = _read32(regs, 4)         # 40734+40735

        # ── Block 3c: HK1 Heizkurve-Sollwerte (40117-40121, 5 Reg.) ──────────
        if (regs := await self._read_block(117, 5)) is not None:
            if regs[0] not in _SENTINEL: data["hk1_vl_soll_20at"]  = regs[0]   # 40117
            if regs[1] not in _SENTINEL: data["hk1_vl_soll_5at"]   = regs[1]   # 40118
            if regs[2] not in _SENTINEL: data["hk1_vl_soll_m10at"] = regs[2]   # 40119
            if regs[3] not in _SENTINEL: data["hk1_max_vl"]         = regs[3]   # 40120
            if regs[4] not in _SENTINEL: data["hk1_min_vl"]         = regs[4]   # 40121

        # ── Block 4: WÜST-Funktion + Betriebsmodi (40215-40244, 30 Reg.) ──
        if (regs := await self._read_block(215, 30)) is not None:
            if (v := _status(regs[0]))  is not None: data["funktion_wuest"]    = v   # 40215
            if (v := _status(regs[25])) is not None: data["betriebsmodus_hk0"] = v   # 40240
            if (v := _status(regs[26])) is not None: data["betriebsmodus_hk1"] = v   # 40241
            if (v := _status(regs[27])) is not None: data["betriebsmodus_hk2"] = v   # 40242
            if (v := _status(regs[28])) is not None: data["betriebsmodus_hk3"] = v   # 40243

        return data

    async def async_write_register(self, pdf_register: int, value: int) -> None:
        """Schreibt einen Holding-Register-Wert.

        Reihenfolge: zuerst FC16 (write multiple registers), dann als Fallback
        FC06 (write single register), falls das Gerät FC16 ablehnt oder nicht
        beantwortet.

        Ob der Regler den Wert wirklich übernimmt, lässt sich erst nach einer
        Weile sagen: Das CM12 schreibt zuerst in sein Spiegelregister und reicht
        die Änderung danach an den Regler weiter. Der Schreibvorgang wird deshalb
        vorgemerkt und beim ersten Poll nach ``WRITE_VERIFY_DELAY`` Sekunden
        geprüft (siehe ``_verify_pending_writes``).

        Wirft ``HomeAssistantError``, wenn der Schreibvorgang auf Modbus-Ebene
        fehlschlägt, damit der Fehler in der Oberfläche sichtbar wird.
        """
        address = pdf_register - 40000  # PDF-Registernummer → Modbus-Adresse
        try:
            try:
                await self.unit.write_registers(address, [value])
            except (IllegalFunctionError, ModbusTimeoutError) as err:
                _LOGGER.debug(
                    "FC16 auf Register %s fehlgeschlagen (%s), versuche FC06",
                    pdf_register, err,
                )
                await self.unit.write_register(address, value)

            # Sofortige Rücklesung: zeigt nur, ob das CM12 den Wert in sein
            # Spiegelregister übernommen hat – nicht, ob der Regler ihn hält.
            if (regs := await self._read_block(address, 1)) is not None:
                _LOGGER.debug(
                    "Register %s: geschrieben %s, sofort gelesen %s",
                    pdf_register, value, regs[0],
                )
        except ModbusExceptionError as err:
            raise HomeAssistantError(
                f"Gerät hat das Schreiben von Register {pdf_register} "
                f"(Wert {value}) abgelehnt: {err}"
            ) from err
        except ModbusError as err:
            raise HomeAssistantError(
                f"Fehler beim Schreiben von Register {pdf_register}: {err}"
            ) from err

        self._pending_writes[address] = _PendingWrite(
            pdf_register=pdf_register,
            value=value,
            written_at=time.monotonic(),
        )
