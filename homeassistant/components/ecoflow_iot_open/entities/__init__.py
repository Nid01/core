"""EcoFlow IoT Open entity module."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from functools import cached_property
import time
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from ..api import EcoFlowIoTOpenAPIInterface
from ..const import DOMAIN, ECOFLOW

# from ..products import EcoFlowDeviceInfo


class EcoFlowBaseEntity(Entity):
    """Define a base entity."""

    _attr_should_poll = False

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: Any,  # dict[str, Any],
        mqtt_key: str,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:  # object:
        """Initialize."""
        self.hass = api.hass

        if title == "":
            title = mqtt_key

        self._api = api
        self._attr_available = False
        self._attr_entity_registry_enabled_default = enabled
        self._attr_name = title
        # f"{device.device_name} {title}"
        # f"{device.device_name}_{mqtt_key}"
        unique_id = f"{device.serial_number}_{mqtt_key}"
        self._attr_unique_id = unique_id
        # self._attr_unique_id = f"{device.serial_number}_{device.device_name}"
        # self._attr_unique_id = self.gen_unique_id(device.serial_number, mqtt_key)
        self._auto_enable = auto_enable
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.serial_number)},
            manufacturer=ECOFLOW,
            model=device.model,
            name=device.device_name,
            serial_number=device.serial_number,
        )
        self._device = device

        self._last_update_time: float = 0.0
        self._mqtt_key = mqtt_key
        self._update_callback: Callable[[], None] | None = None
        self.__attributes_mapping: dict[str, str] = {}

        self.__attrs = OrderedDict[str, Any]()

    @staticmethod
    def gen_unique_id(sn: str, key: str):
        """Generate unique id for entity."""
        return "ecoflow-" + sn + "-" + key.replace(".", "-").replace("_", "-")

    def attr(
        self,
        mqtt_key: str,
        title: str = "",
        default: Any = None,
    ) -> EcoFlowBaseEntity:
        """Add attribute to entity."""
        if title == "":
            title = mqtt_key
        self.__attributes_mapping[mqtt_key] = title
        self.__attrs[title] = default
        return self

    async def async_added_to_hass(self) -> None:
        """Subscribe to device events."""
        await super().async_added_to_hass()
        disposableBase = self._api.data_holder.params_observable().subscribe(
            self._updated
        )
        self.async_on_remove(disposableBase.dispose)

        # self.async_on_remove(
        #     async_dispatcher_connect(self.hass, PUSH_UPDATE, self.on_update_received)
        # )

    def _updated(self, data: dict[str, Any]):
        """Update attributes and values."""
        if data.get(self.serial_number):
            # update attributes
            for key, title in self.__attributes_mapping.items():
                if key in data:
                    self.__attrs[title] = data[key]

            # update value
            if self._mqtt_key in data[self.serial_number]:
                self._attr_available = True
                if self._auto_enable:
                    self._attr_entity_registry_enabled_default = True

                if self._update_value(data[self.serial_number][self._mqtt_key]):
                    self._attr_available = True
                    self._last_update_time = time.time()
                    self.schedule_update_ha_state()

    # def update_status(self):
    #     # if status == "online":
    #     #     # self._attr_state = "online"
    #     #     # self._update_value(True)
    #     #     self._attr_available = True
    #     # else:
    #     #     # self._attr_state = "offline"
    #     #     # self._update_value(False)
    #     #     self._attr_available = False
    #     #     self.hass = (
    #     #         self._api._hass
    #     #     )  # Why is self.hass None even though it has been set during __init__?
    #     self.hass = self._api.hass
    #     self.async_write_ha_state()

    def _update_value(self, val: Any) -> bool:
        return False

    @callback
    def on_update_received(self) -> None:
        """Update was pushed from the EcoFlow API."""
        self.schedule_update_ha_state()

    # @property
    # @cached_property
    # def available(self) -> bool:
    #     """Return if the device is online or not."""
    #     if isinstance(self._attr_device_info, dict):
    #         return self._attr_device_info.get("status", False)
    #     return False

    def set_update_callback(self, update_callback: Callable[[], None]) -> None:
        """Set callback to run when state changes."""
        self._update_callback = update_callback

    # @cached_property
    # def device_info(self) -> DeviceInfo:
    #     """Return device registry information for this entity."""
    #     return DeviceInfo(
    #         identifiers={(DOMAIN, self._device.serial_number)},
    #         manufacturer="EcoFlow",
    #         name=self._device.device_name,
    #         model=self._device.model,
    #     )

    @cached_property
    def serial_number(self) -> str:
        """Return serial number of EcoFlow device."""
        if isinstance(self._attr_device_info, dict):
            serial_number = self._attr_device_info.get("serial_number", "")
            if isinstance(serial_number, str):
                return serial_number
        return ""


class EcoFlowBaseCommandEntity(EcoFlowBaseEntity):
    """Define a base command entity."""

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: Any,  # dict[str, Any],
        mqtt_key: str,
        command: Callable[[int], dict[str, Any]],
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize."""
        super().__init__(api, device, mqtt_key, title, enabled, auto_enable)
        self._command = command

    async def send_set_message(self, target_value: Any, command: dict):
        """Send set message for EcoFlow device."""
        await self._api.publish(self.serial_number, command)

    def command_dict(self, value: int) -> dict[str, Any]:
        """Return command dictionary."""
        # if self._command:
        # p_count = len(inspect.signature(self._command).parameters)
        # if p_count == 1:
        return self._command(value)
        # if p_count == 2:
        #     return self._command(value, self._api.data_holder.params)

        # return None
