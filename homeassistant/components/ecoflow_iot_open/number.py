"""EcoFlow IoT Open number module."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.components.number import (
    DOMAIN as NUMBER_DOMAIN,
    NumberEntity,
    NumberMode,
)
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEGREE, LIGHT_LUX, PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import EcoFlowIoTOpenAPIInterface
from .const import API_CLIENT, DOMAIN, PRODUCTS
from .entity import EcoFlowBaseCommandEntity
from .products import BaseDevice, ProductType

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up numbers based on a config entry."""

    api: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][
        config_entry.entry_id
    ]
    products: dict[ProductType, dict[str, BaseDevice]] = hass.data[DOMAIN][PRODUCTS][
        config_entry.entry_id
    ]

    numbers: list = []
    for devices in products.values():
        for device in devices.values():
            numbers.extend(device.numbers(api))

    if numbers:
        async_add_entities(numbers)


class BaseNumberEntity(NumberEntity, EcoFlowBaseCommandEntity):
    """Base number entity."""

    # _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        min_value: int,
        max_value: int,
        command: Callable[[int], dict[str, Any]] | Callable[[Any, Any], dict[str, Any]],
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize."""
        super().__init__(api, device, mqtt_key, command, title, enabled, auto_enable)
        self._attr_native_max_value = max_value
        self._attr_native_min_value = min_value
        self.entity_id = f"{NUMBER_DOMAIN}.{device.device_name.replace(' ', '_').replace('-', '_').replace('.', '_')}_{mqtt_key}"

    def _update_value(self, val: Any) -> bool:
        if self._attr_native_value != val:
            self._attr_native_value = val
            return True
        return False


class ValueUpdateNumberEntity(BaseNumberEntity):
    """Number value update entity."""

    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        await self.send_set_message(self.command_dict(int(value)))


class AngleNumberEntity(ValueUpdateNumberEntity):
    """Angle number entity."""

    _attr_icon = "mdi:format-text-rotation-angle-up"

    _attr_native_unit_of_measurement = DEGREE
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(val + 10)


class LevelNumberEntity(ValueUpdateNumberEntity):
    """Level number entity."""

    _attr_native_unit_of_measurement = PERCENTAGE


class BatteryNumberEntity(LevelNumberEntity):
    """Battery level number entity."""

    _attr_icon = "battery-charging-100"

    @property
    def icon(self) -> str:
        """Icon for battery level."""
        if isinstance(self.state, int):
            rounded_brightness = round(self.state / 10) * 10
            if 5 <= rounded_brightness <= 94:
                return "mdi:battery-charging-" + str(rounded_brightness)
            if rounded_brightness < 5:
                return "mdi:battery-charging-outline"
            if rounded_brightness > 94:
                return "mdi:battery-charging-100"
        return "mdi:battery-charging-100"


class BrightnessNumberEntity(LevelNumberEntity):
    """Brightness level number entity."""

    _attr_icon = "mdi:lightbulb-on"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(round(max(0, min(100, val / 1023 * 100))))

    @property
    def icon(self) -> str:
        """Icon for brightness level."""
        if isinstance(self.state, int):
            rounded_brightness = round(self.state / 10) * 10
            if 5 <= rounded_brightness <= 94:
                return "mdi:lightbulb-on-" + str(rounded_brightness)
            if rounded_brightness < 5:
                return "mdi:lightbulb-outline"
        return "mdi:lightbulb-on"


class MinimumLightIntesityNumberEntity(ValueUpdateNumberEntity):
    """Minimum light intensity number entity."""

    _attr_icon = "mdi:brightness-1"

    _attr_native_unit_of_measurement = LIGHT_LUX
    _attr_native_step = 5000
    _attr_mode = NumberMode.BOX

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        value = int(value)

        # Check if device_entry is valid
        if not self.device_entry or not self.device_entry.name:
            _LOGGER.error(
                "Device entry or device name is missing for entity %s", self.entity_id
            )
            return

        # Get the state of the related select entity
        state = self.hass.states.get(
            f"{SELECT_DOMAIN}.{self.device_entry.name.replace(' ', '_').lower()}_iot_lightsen"
        )

        if state and "options" in state.attributes:
            try:
                # Find the index of the current state in the options list
                index = list(state.attributes["options"]).index(state.state)
                await self.send_set_message(self.command_dict({value, index}))
            except ValueError:
                _LOGGER.error(
                    "State '%s' not found in options for entity %s",
                    state.state,
                    state.entity_id,
                )
        else:
            _LOGGER.error("State or options not found for entity %s", self.entity_id)

    @property
    def icon(self) -> str:
        """Icon for minimum light intensity."""

        if isinstance(self.state, int):
            if self.state == 10000:
                return "mdi:brightness-1"
            if self.state == 15000:
                return "mdi:brightness-5"
            if self.state == 20000:
                return "mdi:brightness-6"
            if self.state == 25000:
                return "mdi:brightness-4"
            if self.state == 30000:
                return "mdi:brightness-7"
        return "mdi:brightness-1"


class PowerNumberEntity(ValueUpdateNumberEntity):
    """Power number entity."""

    _attr_icon = "mdi:flash"  # "mdi:transmission-tower-import"

    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    # _attr_device_class = SensorDeviceClass.POWER

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(round(val / 10))
