"""Base device for EcoFlow products."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

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
        self._available = bool(device_info.get("online"))
        self._api = api_interface
        self._device_info: dict[str, Any] = device_info
        self._model: str

    def set_availability(self, available: bool) -> None:
        """Set availability status for the device."""
        self._available = available

    def remove_unnecessary_keys(self, keys: set) -> set:
        """Remove unnecessary device info keys from set."""
        keys.remove("deviceName")
        keys.remove("online")
        keys.remove("productName")
        keys.remove("sn")
        return keys

    @abstractmethod
    def sensors(self, api) -> Sequence[SensorEntity]:  # Sequence[BaseSensorEntity]:
        """Return a empty list of SensorEntityDescription."""

    @abstractmethod
    def switches(self, api) -> Sequence[SwitchEntity]:  # Sequence[BaseSwitchEntity]:
        """Return a empty list of SwitchEntity."""

    @abstractmethod
    def numbers(self, api) -> Sequence[NumberEntity]:  # Sequence[BaseNumberEntity]:
        """Return a empty list of NumberEntity."""

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
        return str(self._device_info.get("deviceName", self.model))

    @property
    def model(self) -> str:
        """Return the model name."""
        return self._model

    def is_available(self) -> bool:
        """Return the current device availability."""
        if self._api.data_holder.params.get(self.serial_number):
            if not self._api.data_holder.params[self.serial_number]["status"]:
                return False
        return self._available
