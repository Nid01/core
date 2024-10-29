"""Base device for EcoFlow products."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity

from ..const import (
    DELTA_MAX,
    POWERSTREAM,
    SINGLE_AXIS_SOLAR_TRACKER,
    SMART_PLUG,
    ProductType,
)

_LOGGER = logging.getLogger(__name__)


class BaseDevice(ABC):
    """Base device for EcoFlow products."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        self._api = api_interface
        self._device_info: dict[str, Any] = device_info
        self._update_callback = None
        self._model: str
        # self.device_name: str

    def set_update_callback(self, callback) -> None:
        """Set update callback for the device."""
        self._update_callback = callback

    def update_device_info(self, update: dict[str, Any]) -> None:
        """Take a dictionary and update the stored _device_info based on the present dict fields."""
        _set = False
        _json_key: str
        if self.type in (
            ProductType.POWERSTREAM,
            ProductType.SINGLE_AXIS_SOLAR_TRACKER,
            ProductType.SMART_PLUG,
        ):
            _json_key = "param"
        else:
            _json_key = "params"

        if update.get("addr"):
            _prefix = str(update.get("addr")) + "."
        else:
            _prefix = ""

        try:
            for key, value in update[_json_key].items():
                if isinstance(value, dict):
                    for _key, _value in value.items():
                        self._device_info[key][_key] = _value
                elif key == "status":
                    self._device_info["online"] = value
                else:
                    self._device_info[_prefix + key] = value
                _set = True

            if self._update_callback is not None and _set:
                _LOGGER.debug("Calling the call back to notify updates have occurred")
                self._update_callback()
        except Exception:  # pylint: disable=broad-exception-caught
            _LOGGER.error(
                msg=("Failed to update with message: %d", update), stack_info=True
            )

    @abstractmethod
    def sensors(self, dataHolder) -> Sequence[SensorEntity]:
        """Return a empty list of SensorEntityDescription."""
        # pass

    @staticmethod
    def _get_productType_for_sn_prefix(value: str) -> ProductType:
        """Return a proper type from a string input."""
        _serial_number = value[:4]
        if _serial_number == DELTA_MAX:
            return ProductType.DELTA_MAX
        if _serial_number == SINGLE_AXIS_SOLAR_TRACKER:
            return ProductType.SINGLE_AXIS_SOLAR_TRACKER
        if _serial_number == POWERSTREAM:
            return ProductType.POWERSTREAM
        if _serial_number == SMART_PLUG:
            return ProductType.SMART_PLUG
        _LOGGER.error("Unknown device type state: %s", value)
        return ProductType.UNKNOWN

    @property
    def serial_number(self) -> str:
        """Return the device serial number."""
        return str(self._device_info.get("sn"))

    @property
    def type(self) -> ProductType:
        """Return the ProductType of the device."""
        return self._get_productType_for_sn_prefix(self.serial_number)

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
        """Return the model name."""
        return self._model
