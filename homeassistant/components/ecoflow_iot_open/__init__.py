"""The EcoFlow IoT Open integration."""

from collections import OrderedDict
from collections.abc import Callable
from datetime import timedelta
from functools import cached_property
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import dispatcher_send

from .api import EcoFlowIoTOpenAPIInterface
from .const import API_CLIENT, CONF_ACCESS_KEY, CONF_SECRET_KEY, DOMAIN, PRODUCTS
from .errors import (
    ClientError,
    EcoFlowIoTOpenError,
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
)
from .products import Device, ProductType

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]
PUSH_UPDATE = "ecoflow_iot_open.push_update"

INTERVAL = timedelta(minutes=60)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up EcoFlow IoT Open from a config entry."""

    accessKey = config_entry.data[CONF_ACCESS_KEY]
    secretKey = config_entry.data[CONF_SECRET_KEY]

    try:
        api = await EcoFlowIoTOpenAPIInterface.certification(accessKey, secretKey)
    except (InvalidCredentialsError, KeyError):
        _LOGGER.error("Invalid credentials provided")
        return False
    except EcoFlowIoTOpenError as err:
        raise ConfigEntryNotReady from err

    try:
        products = await api.get_devices_by_product(
            [
                ProductType.DELTA_MAX,
                ProductType.POWERSTREAM,
                ProductType.SINGLE_AXIS_SOLAR_TRACKER,
                ProductType.SMART_PLUG,
            ]
        )
    except (ClientError, GenericHTTPError, InvalidResponseFormat) as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {API_CLIENT: {}, PRODUCTS: {}})
    hass.data[DOMAIN][API_CLIENT][config_entry.entry_id] = api
    hass.data[DOMAIN][PRODUCTS][config_entry.entry_id] = products

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    await api.connect()

    def update_published():
        """Handle a push update."""
        dispatcher_send(hass, PUSH_UPDATE)

    for devices in products.values():
        for device in devices.values():
            device.set_update_callback(update_published)

    # async def resubscribe(now):
    #     """Resubscribe to MQTT updates."""
    #     await hass.async_add_executor_job(api.unsubscribe)
    #     api.subscribe()

    #     # refresh even required?
    #     # await asyncio.sleep(60)
    #     # await api.refresh_devices()

    # config_entry.async_on_unload(async_track_time_interval(hass, resubscribe, INTERVAL))

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    ):
        # api: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][
        #     config_entry.entry_id
        # ]
        # api.disconnect()
        hass.data[DOMAIN][API_CLIENT].pop(config_entry.entry_id)
        hass.data[DOMAIN][PRODUCTS].pop(config_entry.entry_id)

    return unload_ok


class EcoFlowIotOpenEntity(SensorEntity):
    """Define a base EcoFlow Iot Open entity."""

    _attr_should_poll = False

    def __init__(
        self,
        client: EcoFlowIoTOpenAPIInterface,
        device: Device,
        mqtt_key: str,
        auto_enable: bool = False,
    ) -> None:
        """Initialize."""
        self._attr_name = device.device_name
        self._attr_unique_id = f"{device.serial_number}_{device.device_name}"
        self._auto_enable = auto_enable
        self._client = client
        self._device = device
        self._mqtt_key = mqtt_key
        self._update_callback: Callable[[], None] | None = None
        self.__attributes_mapping: dict[str, str] = {}
        self.__attrs = OrderedDict[str, Any]()

    async def async_added_to_hass(self) -> None:
        """Subscribe to device events."""
        await super().async_added_to_hass()
        disposableBase = self._client.data.params_observable().subscribe(self._updated)
        self.async_on_remove(disposableBase.dispose)

        # self.async_on_remove(
        #     async_dispatcher_connect(self.hass, PUSH_UPDATE, self.on_update_received)
        # )

    def _updated(self, data: dict[str, Any]):
        """Update attributes and values."""
        if data.get(self._device.serial_number):
            # update attributes
            for key, title in self.__attributes_mapping.items():
                if key in data:
                    self.__attrs[title] = data[key]

            # update value
            if self._mqtt_key in data[self._device.serial_number]:
                self._attr_available = True
                if self._auto_enable:
                    self._attr_entity_registry_enabled_default = True

                if self._update_value(data[self._device.serial_number][self._mqtt_key]):
                    self.async_write_ha_state()

    def _update_value(self, val: Any) -> bool:
        if self._attr_native_value != val:
            self._attr_native_value = val
            return True
        return False

    # def _update_value(self, val: Any) -> bool:
    #     return False

    @callback
    def on_update_received(self) -> None:
        """Update was pushed from the EcoFlow API."""
        self.async_write_ha_state()

    # @cached_property
    # def available(self) -> bool:
    #     """Return if the device is online or not."""
    #     return self._EcoFlowIotOpen.online

    @cached_property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.serial_number)},
            manufacturer="EcoFlow",
            name=self._device.device_name,
            model=self._device.model,
        )

    def set_update_callback(self, update_callback: Callable[[], None]) -> None:
        """Set callback to run when state changes."""
        self._update_callback = update_callback
