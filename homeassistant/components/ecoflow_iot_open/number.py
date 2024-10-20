"""EcoFlow IoT Open number module."""

from __future__ import annotations

from collections.abc import Callable
from functools import cached_property
from typing import Any

from homeassistant.components.number import (
    DOMAIN as NUMBER_DOMAIN,
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import EcoFlowIoTOpenAPIInterface
from .const import API_CLIENT, DOMAIN, PRODUCTS
from .entities import EcoFlowBaseCommandEntity
from .products import BaseDevice, ProductType


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
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
        command: Callable[[int], dict[str, Any]],
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

            if hasattr(self, "icon"):
                del self.icon  # invalidate cached icon because doesn't update properly
            return True
        return False


class ValueUpdateEntity(BaseNumberEntity):
    """Number value update entity."""

    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        # if self._command:
        ival = int(value)
        await self.send_set_message(ival, self.command_dict(ival))


class LevelEntity(ValueUpdateEntity):
    """Level number entity."""

    _attr_native_unit_of_measurement = PERCENTAGE


class BatteryLevelEntity(LevelEntity):
    """Battery level number entity."""

    _attr_icon = "battery-charging-100"

    @cached_property
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


class BrightnessEntity(LevelEntity):
    """Brightness level number entity."""

    _attr_icon = "mdi:lightbulb-on"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(round(max(0, min(100, val / 1023 * 100))))

    @cached_property
    def icon(self) -> str:
        """Icon for brightness level."""
        if isinstance(self.state, int):
            rounded_brightness = round(self.state / 10) * 10
            if 5 <= rounded_brightness <= 94:
                return "mdi:lightbulb-on-" + str(rounded_brightness)
            if rounded_brightness < 5:
                return "mdi:lightbulb-outline"
        return "mdi:lightbulb-on"


class PowerEntity(ValueUpdateEntity):
    """Power number entity."""

    _attr_icon = "mdi:flash"  # "mdi:transmission-tower-import"

    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    # _attr_device_class = SensorDeviceClass.POWER

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(round(val / 10))
