"""Constants for the EcoFlow IoT Open integration."""

from collections.abc import Callable
from enum import Enum
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


DOMAIN = "ecoflow_iot_open"
API_CLIENT = "api_client"
DEVICES = "devices"

CONF_ACCESS_KEY = "access_key"
CONF_SECRET_KEY = "secret_key"

SIGNAL_ECOFLOW_IOT_OPEN_UPDATE_RECEIVED = "ecoflow_iot_open_update_received_{}_{}"

DELTA_MAX = "DAEB"  # productType = 13
# Potentially setup DELTA_MAX_SMART_EXTRA_BATTERY as separate device?
# DELTA_MAX_SMART_EXTRA_BATTERY = "E2AB"  # productType=13
POWERSTREAM = "HW51"  # productType=75
SMART_PLUG = "HW52"
SINGLE_AXIS_SOLAR_TRACKER = "HZ31"
# More SN-prefixes required

SERIAL_NUMBER = "sn"
NAME = "deviceName"
STATUS = "online"


class EcoFlowProductType(Enum):
    """Define the equipment product type by DeviceSN-prefix."""

    DELTA_2 = 1
    RIVER_2 = 2
    RIVER_2_MAX = 3
    RIVER_2_PRO = 4
    DELTA_PRO = 5
    RIVER_MAX = 6
    RIVER_PRO = 7
    DELTA_MAX = 8  # productType = 13
    DELTA_2_MAX = 9  # productType = 81
    DELTA_MINI = 15  # productType = 15
    SINGLE_AXIS_SOLAR_TRACKER = 31
    WAVE_2 = 45  # productType = 45
    GLACIER = 46
    POWERSTREAM = 51
    SMART_PLUG = 52
    DIAGNOSTIC = 99


class EcoFlowDevice:
    """Define a EcoFlow device."""

    def __init__(self, device_info: dict[str, Any]) -> None:
        """Initialize."""
        self.device_info: dict[str, Any] = device_info
        self._update_callback = None
        self._callbacks: list = []

    def set_update_callback(self, callback):
        """Set update callback."""
        self._update_callback = callback

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when the Equipment changes state."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callbacks."""
        self._callbacks.remove(callback)

    def update_device_info(self, update: dict):
        """Take dictionary and update the stored _equipment_info based on the present dict fields."""
        _set = False
        if "params" in update:
            quota: dict = update["params"]
        else:
            quota = update
        for key, value in quota.items():
            # _LOGGER.debug("Before update %s : %s", key, self._equipment_info.get("key"))
            # try:
            if isinstance(value, dict):
                for _key, _value in value.items():
                    self.device_info[key][_key] = _value
                    # _LOGGER.debug("Updating [%s][%s] = %s", key, _key, _value)
            elif isinstance(self.device_info.get(key), dict):
                if self.device_info[key].get("value") is not None:
                    self.device_info[key]["value"] = value
                    # _LOGGER.debug("Updating [%s][value] = %s", key, value)
            else:
                self.device_info[key] = value
                # _LOGGER.debug("Updating [%s] = %s", key, value)
            # except Exception:
            #     _LOGGER.error("Failed to update with message: %s", update)
            # _LOGGER.debug("After update %s : %s", key, self._equipment_info.get(key))
            _set = True

        if self._update_callback is not None and _set:
            # _LOGGER.debug("Calling the call back to notify updates have occurred")
            self._update_callback()

    #     @staticmethod
    #     def _coerce_type_from_string(value: str) -> EcoFlowProductType:
    #         """Return a proper type from a string input."""
    #         if value == DELTA_MAX:
    #             return EcoFlowProductType.DELTA_MAX
    #         elif value == POWERSTREAM:
    #             return EcoFlowProductType.POWERSTREAM
    #         elif value == SMART_PLUG:
    #             return EcoFlowProductType.SMART_PLUG
    #         elif value == SINGLE_AXIS_SOLAR_TRACKER:
    #             return EcoFlowProductType.SINGLE_AXIS_SOLAR_TRACKER
    #         else:
    #             _LOGGER.error("Unknown equipment type state: %s", value)
    #             return EcoFlowProductType.DIAGNOSTIC

    @property
    def serial_number(self) -> str:
        """Return the equipment serial number."""
        return str(self.device_info.get(SERIAL_NUMBER))

    @property
    def name(self) -> str:
        """Return the equipment name."""
        return str(self.device_info.get(NAME))

    @property
    def status(self) -> str:
        """Return the equipment status."""
        return str(self.device_info.get(STATUS))
