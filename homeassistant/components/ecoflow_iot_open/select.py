"""EcoFlow IoT Open select module."""

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN, SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import slugify

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
        command: Callable[[], dict[str, Any]]
        | Callable[[Any], dict[str, Any]]
        | Callable[[Any, Any], dict[str, Any]],
        options: list[str] | dict[str, int],
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize."""
        super().__init__(api, device, mqtt_key, command, title, enabled, auto_enable)
        self.entity_id = (
            f"{SELECT_DOMAIN}.{slugify(f'{device.device_name}_{mqtt_key}')}"
        )

        if mqtt_key == "iot.switchState":
            unique_id = f"{device.serial_number}_{mqtt_key}_{slugify(title)}"
        else:
            unique_id = f"{device.serial_number}_{mqtt_key}"
        self._attr_unique_id = unique_id
        self._attr_options = (
            list(options.keys()) if isinstance(options, dict) else options
        )
        self._attr_current_option = None
        self._options_dict = options

    def _update_value(self, val: Any) -> bool:
        if self._attr_name in (
            "iot.supplyPriority",
            "inv.cfgStandbyMin",
            "pd.standByMode",
            "pd.lcdOffSec",
        ):
            ival = int(val)
            if isinstance(self._options_dict, dict):
                lval = [k for k, v in self._options_dict.items() if v == ival]
                if len(lval) == 1:
                    self._attr_current_option = lval[0]
                    return True
                return False
            return False

        val = val - 1

        if 0 <= val < len(self._attr_options):
            if self._attr_current_option != self._attr_options[val]:
                self._attr_current_option = self._attr_options[val]
            return True
        return False

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""

        if self._attr_name in ("pd.standByMode", "pd.lcdOffSec", "inv.cfgStandbyMin"):
            if isinstance(self._options_dict, dict):
                val = self._options_dict[option]
                await self.send_set_message(self.command_dict(int(val)))
        elif option in self._attr_options:
            index = self._attr_options.index(option)
            self._attr_current_option = option
            await self.send_set_message(self.command_dict(index))


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
                    self.command_dict({index + 1, int(state.state)})
                )
            else:
                _LOGGER.warning(
                    "State for entity %s is unavailable or invalid", self.entity_id
                )

    @property
    def icon(self) -> str:
        """Icon for light tracking sensitivity."""

        if self.state in self._attr_options:
            index = self._attr_options.index(self.state)
            if index == 1:
                return "mdi:brightness-5"
            if index == 2:
                return "mdi:brightness-6"
            if index == 3:
                return "mdi:brightness-7"
        return "mdi:brightness-5"


class PowerSupplyPrioritySelectEntity(BaseSelectEntity):
    """Power supply priority select entity."""

    @property
    def icon(self) -> str | None:
        """Return the icon to be used for this entity."""

        if self.state in self._attr_options:
            index = self._attr_options.index(self.state)
            if index == 1:
                return "mdi:battery-charging"
        return "mdi:home-lightning-bolt"


class ScenarioSelectEntity(BaseSelectEntity):
    """Scenario switch."""

    _attr_entity_category = EntityCategory.CONFIG

    def _update_value(self, val: Any) -> bool:
        if 0 <= val < len(self._attr_options):
            if self._attr_current_option != val:
                self._attr_current_option = self._attr_options[val]
            return True
        return False

    @property
    def icon(self) -> str | None:
        """Scenes icon handling."""

        if self.state in self._attr_options:
            index = self._attr_options.index(self.state)
            if index == 1:
                return "mdi:angle-acute"
        return "mdi:format-text-rotation-angle-up"


class WindSensitivitySelectEntity(BaseSelectEntity):
    """Wind sensitivity select entity."""

    _attr_icon = "mdi:weather-windy"

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        if option in self._attr_options:
            index = self._attr_options.index(option)
            self._attr_current_option = option

        await self.send_set_message(self.command_dict(index + 1))

    @property
    def icon(self) -> str:
        """Icon for light tracking sensitivity."""

        if self.state in self._attr_options:
            index = self._attr_options.index(self.state)
            if index == 0:
                return "mdi:fan-speed-1"
            if index == 1:
                return "mdi:fan-speed-2"
            if index == 2:
                return "mdi:fan-speed-3"
        return "mdi:fan-alert"
