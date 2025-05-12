"""EcoFlow IoT Open select module."""

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN, SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import EcoFlowIoTOpenAPIInterface
from .const import API_CLIENT, DOMAIN, PRODUCTS, ProductType
from .entity import EcoFlowBaseCommandEntity
from .products import BaseDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up select based on a config entry."""

    api: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][
        config_entry.entry_id
    ]
    products: dict[ProductType, dict[str, BaseDevice]] = hass.data[DOMAIN][PRODUCTS][
        config_entry.entry_id
    ]

    select: list = []
    for devices in products.values():
        for device in devices.values():
            select.extend(device.selects(api))

    if select:
        async_add_entities(select)


class BaseSelectEntity(SelectEntity, EcoFlowBaseCommandEntity):
    """Define a base select entity."""

    _attr_should_poll = False
    _attr_options = []

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        command: Callable[[int], dict[str, Any]],
        options: list[str],
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize."""
        super().__init__(api, device, mqtt_key, command, title, enabled, auto_enable)
        self.entity_id = f"{SELECT_DOMAIN}.{device.device_name.replace(' ', '_').replace('-', '_').replace('.', '_')}_{mqtt_key}"

        if mqtt_key in ("iot.switchState",):
            unique_id = f"{device.serial_number}_{mqtt_key}_{title.replace(' ', '_').replace('-', '_').replace('.', '_')}"
        else:
            unique_id = f"{device.serial_number}_{mqtt_key}"
        self._attr_unique_id = unique_id
        self._attr_options = options
        self._attr_current_option = None

    def _update_value(self, val: Any) -> bool:
        val = val - 1
        # if isinstance(val, int):
        if 0 <= val < len(self._attr_options):
            if self._attr_current_option != val:
                self._attr_current_option = self._attr_options[val]
            return True
        return False


class LightTrackingSensitivitySelectEntity(BaseSelectEntity):
    """Light tracking sensitivity select entity."""

    _attr_icon = "mdi:brightness-5"

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        if option in self._attr_options:
            index = self._attr_options.index(option)
            self._attr_current_option = option

            state = self.hass.states.get(
                f"{NUMBER_DOMAIN}.{self.device_entry.name.replace(' ', '_').lower()}_iot_strlux"
                if self.device_entry and self.device_entry.name
                else ""
            )

            if state and state.state.isdigit():
                await self.send_set_message(
                    index + 1, self.command_dict({index + 1, int(state.state)})
                )
            else:
                _LOGGER.warning(
                    "State for entity %s is unavailable or invalid", self.entity_id
                )

    @property
    def icon(self) -> str:
        """Icon for light tracking sensitivity."""

        if isinstance(self.state, int):
            if self.state == 1:
                return "mdi:brightness-5"
            if self.state == 2:
                return "mdi:brightness-6"
            if self.state == 3:
                return "mdi:brightness-7"
        return "mdi:brightness-5"


class WindSensitivitySelectEntity(BaseSelectEntity):
    """Wind sensitivity select entity."""

    _attr_icon = "mdi:weather-windy"

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        if option in self._attr_options:
            index = self._attr_options.index(option)
            self._attr_current_option = option

        await self.send_set_message(index + 1, self.command_dict(index + 1))
