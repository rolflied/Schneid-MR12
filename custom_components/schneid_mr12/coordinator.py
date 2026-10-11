"""DataUpdateCoordinator für Schneid MR-12 über Modbus TCP."""

import asyncio
import logging
from datetime import timedelta
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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


class SchneidModbusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Koordinator für alle Modbus-Lesevorgänge."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        slave_id: int,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self._client: AsyncModbusTcpClient | None = None
        # Serialisiert Lesen und Schreiben: der pymodbus-Client darf keine zwei
        # Anfragen gleichzeitig auf einer Verbindung haben, und viele CM12-/
        # Modbus-Gateways verarbeiten ohnehin nur eine Anfrage pro Zeit.
        self._io_lock = asyncio.Lock()

    async def _get_client(self) -> AsyncModbusTcpClient:
        """Gibt einen verbundenen Client zurück – stellt bei Bedarf neu her."""
        if self._client is None or not self._client.connected:
            if self._client is not None:
                self._client.close()
            self._client = AsyncModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=10,
            )
            if not await self._client.connect():
                self._client = None
                raise UpdateFailed(
                    f"Keine Verbindung zu {self.host}:{self.port} möglich"
                )
        return self._client

    async def _rhr(
        self, client: AsyncModbusTcpClient, address: int, count: int
    ):
        """Ruft read_holding_registers versionssicher auf.

        Reihenfolge der Versuche:
        - 3.8+: device_id= (pymodbus 3.8+, count als Keyword)
        - 3.0–3.7: slave= als Keyword
        - 2.x: unit= als Keyword
        - Fallback: kein Slave-Parameter
        """
        for kw in (
            {"count": count, "device_id": self.slave_id},
            {"count": count, "slave": self.slave_id},
            {"count": count, "unit": self.slave_id},
            {"count": count},
        ):
            try:
                return await client.read_holding_registers(address, **kw)
            except TypeError:
                continue
        # pymodbus < 3.8: address + count positional
        for kw in (
            {"device_id": self.slave_id},
            {"slave": self.slave_id},
            {"unit": self.slave_id},
            {},
        ):
            try:
                return await client.read_holding_registers(address, count, **kw)
            except TypeError:
                continue
        raise UpdateFailed("Inkompatible pymodbus-Version – keine passende read_holding_registers-Signatur")

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with self._io_lock:
                client = await self._get_client()
                return await self._read_all(client)
        except UpdateFailed:
            raise
        except ModbusException as err:
            self._client = None
            raise UpdateFailed(f"Modbus-Fehler: {err}") from err
        except Exception as err:
            self._client = None
            raise UpdateFailed(f"Fehler beim Lesen: {err}") from err

    async def _read_all(self, client: AsyncModbusTcpClient) -> dict[str, Any]:
        """Liest alle benötigten Register-Blöcke und gibt ein Daten-Dict zurück."""
        data: dict[str, Any] = {}

        # ── Block 1a: Haupttemperaturen + Heizkreis 0 + 1 (40600-40629, 30 Reg.) ──
        r = await self._rhr(client, 600, 30)
        if not r.isError():
            regs = r.registers
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
        r = await self._rhr(client, 630, 19)
        if not r.isError():
            regs = r.registers
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
        # Hinweis: 40730+ existieren auf diesem Gerät nicht (exc=4).
        # Wärmezählerdaten (40730-40751) sind daher nicht verfügbar.
        r = await self._rhr(client, 690, 40)
        if not r.isError():
            regs = r.registers
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
            if (v := _status(regs[31])) is not None: data["status_pumpe_lm1"] = v
            if (v := _status(regs[32])) is not None: data["status_mischer_lm1"] = v
            if (v := _status(regs[33])) is not None: data["status_pumpe_lm2"] = v
            if (v := _status(regs[34])) is not None: data["status_mischer_lm2"] = v
            if regs[36] not in _SENTINEL: data["reset_counter"]                = regs[36]
            if (v := _temp(regs[38])) is not None: data["aussentemp_mittel"]   = v   # 40728
            if (v := _temp(regs[39])) is not None: data["aussentemp_mittel_lz"] = v  # 40729

        # ── Block 3: Systemparameter + Boilersollwerte (40012-40099, 88 Reg.) ──
        r = await self._rhr(client, 12, 88)
        if not r.isError():
            regs = r.registers
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
        r = await self._rhr(client, 730, 6)
        if not r.isError():
            regs = r.registers
            data["waermemenge_fw"] = _read32(regs, 0) / 10   # 40730+40731
            data["volumen_fw"]     = _read32(regs, 2)         # 40732+40733
            data["leistung_fw"]    = _read32(regs, 4)         # 40734+40735

        # ── Block 3c: HK1 Heizkurve-Sollwerte (40117-40121, 5 Reg.) ──────────
        r = await self._rhr(client, 117, 5)
        if not r.isError():
            regs = r.registers
            if regs[0] not in _SENTINEL: data["hk1_vl_soll_20at"]  = regs[0]   # 40117
            if regs[1] not in _SENTINEL: data["hk1_vl_soll_5at"]   = regs[1]   # 40118
            if regs[2] not in _SENTINEL: data["hk1_vl_soll_m10at"] = regs[2]   # 40119
            if regs[3] not in _SENTINEL: data["hk1_max_vl"]         = regs[3]   # 40120
            if regs[4] not in _SENTINEL: data["hk1_min_vl"]         = regs[4]   # 40121

        # ── Block 4: WÜST-Funktion + Betriebsmodi (40215-40244, 30 Reg.) ──
        r = await self._rhr(client, 215, 30)
        if not r.isError():
            regs = r.registers
            if (v := _status(regs[0]))  is not None: data["funktion_wuest"]    = v   # 40215
            if (v := _status(regs[25])) is not None: data["betriebsmodus_hk0"] = v   # 40240
            if (v := _status(regs[26])) is not None: data["betriebsmodus_hk1"] = v   # 40241
            if (v := _status(regs[27])) is not None: data["betriebsmodus_hk2"] = v   # 40242
            if (v := _status(regs[28])) is not None: data["betriebsmodus_hk3"] = v   # 40243

        return data

    async def _write_fc(
        self, client: AsyncModbusTcpClient, func: str, address: int, payload
    ):
        """Ruft write_register (FC06) bzw. write_registers (FC16) versionssicher auf.

        Gibt die Modbus-Antwort zurück oder ``None``, wenn keine Signatur passt.
        """
        method = getattr(client, func)
        for kw in (
            {"device_id": self.slave_id},
            {"slave": self.slave_id},
            {"unit": self.slave_id},
            {},
        ):
            try:
                return await method(address=address, **payload, **kw)
            except TypeError:
                continue
        return None

    async def async_write_register(self, pdf_register: int, value: int) -> None:
        """Schreibt einen Holding-Register-Wert und prüft, ob er übernommen wurde.

        Reihenfolge: zuerst FC16 (write multiple registers), dann als Fallback
        FC06 (write single register). Viele Schneid-/CM12-Firmwares übernehmen
        Parameteränderungen nur über FC16 zuverlässig.

        Nach dem Schreiben wird das Register zurückgelesen. Übernimmt das Gerät
        den Wert nicht (z. B. weil das CM12 das Spiegelregister beim nächsten
        Regler-Poll wieder überschreibt), wird das als Warnung protokolliert –
        so ist im Log eindeutig sichtbar, ob Lesen oder Gerät das Problem ist.

        Wirft ``HomeAssistantError``, wenn der Schreibvorgang auf Modbus-Ebene
        fehlschlägt, damit der Fehler in der Oberfläche sichtbar wird.
        """
        address = pdf_register - 40000  # PDF-Registernummer → Modbus-Adresse
        try:
            async with self._io_lock:
                client = await self._get_client()

                result = await self._write_fc(
                    client, "write_registers", address, {"values": [value]}
                )
                # Lehnt das Gerät FC16 ab (illegale Funktion), FC06 versuchen.
                if result is None or result.isError():
                    result = await self._write_fc(
                        client, "write_register", address, {"value": value}
                    )

                if result is None:
                    raise HomeAssistantError(
                        "Inkompatible pymodbus-Version – keine passende "
                        "write_register-Signatur gefunden"
                    )
                if result.isError():
                    raise HomeAssistantError(
                        f"Gerät hat das Schreiben von Register {pdf_register} "
                        f"(Adresse {address}, Wert {value}) abgelehnt: {result}"
                    )

                # Rücklesung zur Verifikation (best effort).
                check = await self._rhr(client, address, 1)
                if not check.isError():
                    actual = check.registers[0]
                    if actual != value:
                        _LOGGER.warning(
                            "Register %s (Adresse %s) nach dem Schreiben nicht "
                            "übernommen: geschrieben %s, gelesen %s. Das CM12/der "
                            "Regler hat den Wert nicht persistiert – vermutlich "
                            "erlaubt die Firmware kein direktes Schreiben dieses "
                            "Parameters über Modbus.",
                            pdf_register, address, value, actual,
                        )
        except HomeAssistantError:
            raise
        except Exception as err:
            self._client = None
            raise HomeAssistantError(
                f"Fehler beim Schreiben von Register {pdf_register}: {err}"
            ) from err
