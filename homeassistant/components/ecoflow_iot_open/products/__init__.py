"""Base device for EcoFlow products."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from ..const import SERIAL_NUMBER_PREFIXES, ProductType

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

    async def prepare_protobuf_message(self, command: dict[str, Any]) -> bytes | None:
        """Prepare the protobuf message for the device."""
        return None

    @abstractmethod
    def buttons(self, api) -> Sequence[ButtonEntity]:  # Sequence[BaseButtonEntity]:
        """Return a empty list of SelectEntity."""

    @abstractmethod
    def numbers(self, api) -> Sequence[NumberEntity]:  # Sequence[BaseNumberEntity]:
        """Return a empty list of NumberEntity."""

    @abstractmethod
    def selects(self, api) -> Sequence[SelectEntity]:  # Sequence[BaseSelectEntity]:
        """Return a empty list of SelectEntity."""

    @abstractmethod
    def sensors(self, api) -> Sequence[SensorEntity]:  # Sequence[BaseSensorEntity]:
        """Return a empty list of SensorEntityDescription."""

    @abstractmethod
    def switches(self, api) -> Sequence[SwitchEntity]:  # Sequence[BaseSwitchEntity]:
        """Return a empty list of SwitchEntity."""

    @staticmethod
    def get_product_type_from_serial_number(value: str) -> ProductType:
        """Return the ProductType based on the serial number."""
        serial_number_prefix = value[:4]
        if serial_number_prefix == SERIAL_NUMBER_PREFIXES[ProductType.DELTA_MAX]:
            return ProductType.DELTA_MAX
        if (
            serial_number_prefix
            == SERIAL_NUMBER_PREFIXES[ProductType.SINGLE_AXIS_SOLAR_TRACKER]
        ):
            return ProductType.SINGLE_AXIS_SOLAR_TRACKER
        if serial_number_prefix == SERIAL_NUMBER_PREFIXES[ProductType.POWERSTREAM]:
            return ProductType.POWERSTREAM
        if serial_number_prefix == SERIAL_NUMBER_PREFIXES[ProductType.SMART_PLUG]:
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
        return self.get_product_type_from_serial_number(self.serial_number)

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
