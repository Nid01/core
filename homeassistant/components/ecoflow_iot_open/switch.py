"""EcoFlow IoT Open switch module."""

from collections.abc import Callable
from typing import Any

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import EcoFlowIoTOpenAPIInterface
from .const import API_CLIENT, DOMAIN, PRODUCTS, ProductType
from .entity import EcoFlowBaseCommandEntity
from .products import BaseDevice


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch based on a config entry."""

    api: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][
        config_entry.entry_id
    ]
    products: dict[ProductType, dict[str, BaseDevice]] = hass.data[DOMAIN][PRODUCTS][
        config_entry.entry_id
    ]

    switches: list = []
    for devices in products.values():
        for device in devices.values():
            switches.extend(device.switches(api))

    if switches:
        async_add_entities(switches)


class BaseSwitchEntity(SwitchEntity, EcoFlowBaseCommandEntity):
    """Define a base switch entity."""

    _attr_should_poll = False

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        command: Callable[[int], dict[str, Any]],
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize."""
        super().__init__(api, device, mqtt_key, command, title, enabled, auto_enable)
        if title != "":
            self.entity_id = f"{SWITCH_DOMAIN}.{device.device_name.replace(' ', '_').replace('-', '_').replace('.', '_')}_{title}"
        else:
            self.entity_id = f"{SWITCH_DOMAIN}.{device.device_name.replace(' ', '_').replace('-', '_').replace('.', '_')}_{mqtt_key}"

        if mqtt_key in ("iot.switchState",):
            unique_id = f"{device.serial_number}_{mqtt_key}_{title.replace(' ', '_').replace('-', '_').replace('.', '_')}"
        else:
            unique_id = f"{device.serial_number}_{mqtt_key}"
        self._attr_unique_id = unique_id

    def _update_value(self, val: Any) -> bool:
        if self._attr_is_on != bool(val):
            self._attr_is_on = bool(val)

            # if hasattr(self, "icon"):
            #     del self.icon  # invalidate cached icon because doesn't update properly
            return True
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        # if self._command:
        await self.send_set_message(1, self.command_dict(1))

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        # if self._command:
        await self.send_set_message(0, self.command_dict(0))


class AlignmentModeSwitchEntity(BaseSwitchEntity):
    """Alignment mode switch."""

    @property
    def icon(self) -> str | None:
        """Return the icon to be used for this entity."""
        if self.is_on:
            return "mdi:arrow-oscillating"
        return "mdi:arrow-oscillating-off"


class BeeperSwitchEntity(BaseSwitchEntity):
    """Beeper switch."""

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(val & (1 << 0))

    @property
    def icon(self) -> str:
        """Icon for binary state in context of mqtt key."""
        if self._attr_name in ("beeper", "pd.beepState"):
            if self.state == "on":
                return "mdi:volume-high"
            return "mdi:volume-mute"
        if self.state == "on":
            return "mdi:toggle-switch-variant"
        return "mdi:toggle-switch-variant-off"


class DeviceSwitchEntity(BaseSwitchEntity):
    """Device switch."""

    _attr_icon = "mdi:power"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(val != 0)


class PowerSupplyPriorityEntity(BaseSwitchEntity):
    """Power supply priority switch."""

    @property
    def icon(self) -> str | None:
        """Return the icon to be used for this entity."""
        if self.is_on:
            return "mdi:battery-charging"
        return "mdi:home-lightning-bolt"


class RainProtectionSwitchEntity(BaseSwitchEntity):
    """Switch for rain protection."""

    def _update_value(self, val: Any) -> bool:
        """Check if the second bit is set and update the value."""
        return super()._update_value(val & (1 << 1))

    @property
    def icon(self) -> str:
        """Icon for rain protection sensor."""
        if self.state == "on":
            return "mdi:umbrella-outline"
        return "mdi:umbrella-closed-variant"


class ScenarioSwitchEntity(BaseSwitchEntity):
    """Scenario switch."""

    _attr_entity_category = EntityCategory.CONFIG

    @property
    def icon(self) -> str | None:
        """Scenes icon handling."""
        if self.state == "on":
            return "mdi:angle-acute"
        return "mdi:format-text-rotation-angle-up"


class WindProtectionSwitchEntity(BaseSwitchEntity):
    """Switch for wind protection."""

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(val & (1 << 2))

    @property
    def icon(self) -> str:
        """Icon for wind protection sensor."""
        if self.state == "on":
            return "mdi:windsock"
        return "mdi:weather-windy"
