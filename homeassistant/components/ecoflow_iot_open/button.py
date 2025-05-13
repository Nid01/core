"""EcoFlow IoT Open button module."""

from collections.abc import Callable
from typing import Any

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, ButtonEntity
from homeassistant.config_entries import ConfigEntry
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

    buttons: list = []
    for devices in products.values():
        for device in devices.values():
            buttons.extend(device.buttons(api))

    if buttons:
        async_add_entities(buttons)


class BaseButtonEntity(ButtonEntity, EcoFlowBaseCommandEntity):
    """Define a base button entity."""

    _attr_should_poll = False

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        command: Callable[[], dict[str, Any]],
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize."""
        super().__init__(api, device, "", command, title, enabled, auto_enable)
        self.entity_id = f"{BUTTON_DOMAIN}.{device.device_name.replace(' ', '_').replace('-', '_').replace('.', '_')}_{title}"
        self._attr_unique_id = f"{device.serial_number}_{title}"

    async def async_press(self) -> None:
        """Press the button."""
        await self.send_set_message(command=self.command_dict(None))


class TrackAgainButton(BaseButtonEntity):
    """Define a track again button entity."""

    _attr_icon = "mdi:format-text-rotation-angle-up"
