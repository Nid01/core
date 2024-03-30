"""Define a EcoFlow device."""

from enum import Enum
import logging

_LOGGER = logging.getLogger(__name__)

DELTA_MAX = "DAEB"  # productType = 13
# Potentially setup DELTA_MAX_SMART_EXTRA_BATTERY as separate device?
# DELTA_MAX_SMART_EXTRA_BATTERY = "E2AB"  # productType=13
POWERSTREAM = "HW51"  # productType=75
SMART_PLUG = "HW52"
SINGLE_AXIS_SOLAR_TRACKER = "HZ31"
# More SN-prefixes required


class ProductType(Enum):
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
    UNKNOWN = 100


class Device:
    """Define a device."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        self._api = api_interface
        self._device_info = device_info
        self._update_callback = None

    def set_update_callback(self, callback):
        """Set update callback for the device."""
        self._update_callback = callback

    def update_device_info(self, update: dict):
        """Take a dictionary and update the stored _device_info based on the present dict fields."""
        _set = False
        for key, value in update["params"].items():
            try:
                if isinstance(value, dict):
                    for _key, _value in value.items():
                        self._device_info[key][_key] = _value
                elif key == "status":
                    self._device_info["online"] = value
                else:
                    self._device_info[key] = value
            except Exception:  # pylint: disable=broad-exception-caught
                _LOGGER.error("Failed to update with message: %d", update)
            _set = True

        if self._update_callback is not None and _set:
            _LOGGER.debug("Calling the call back to notify updates have occurred")
            self._update_callback()

    @staticmethod
    def _coerce_type_from_string(value: str) -> ProductType:
        """Return a proper type from a string input."""
        if value[:4] == DELTA_MAX:
            return ProductType.DELTA_MAX
        _LOGGER.error("Unknown device type state: %s", value)
        return ProductType.UNKNOWN

    @property
    def serial_number(self) -> str:
        """Return the device serial number."""
        return str(self._device_info.get("sn"))

    @property
    def type(self) -> ProductType:
        """Return the ProductType of the device."""
        return self._coerce_type_from_string(self.serial_number)

    @property
    def device_name(self) -> str:
        """Return device name."""
        return str(self._device_info.get("deviceName"))

    @property
    def online(self) -> bool:
        """Return if the device is online or not."""
        return self._device_info.get("online", True)

    @property
    def model(self) -> str:
        """Return the value 0-100? of the battery level."""
        return ""
