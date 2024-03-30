"""The EcoFlow IoT Open integration."""

from collections.abc import Callable
from datetime import timedelta
from functools import cached_property
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval

from .api import EcoFlowIoTOpenAPIInterface
from .const import API_CLIENT, CONF_ACCESS_KEY, CONF_SECRET_KEY, DEVICES, DOMAIN
from .devices import Device, ProductType
from .errors import (
    ClientError,
    EcoFlowIoTOpenError,
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
)

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
        devices = await api.get_devices([ProductType.DELTA_MAX])
    except (ClientError, GenericHTTPError, InvalidResponseFormat) as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {API_CLIENT: {}, DEVICES: {}})
    hass.data[DOMAIN][API_CLIENT][config_entry.entry_id] = api
    hass.data[DOMAIN][DEVICES][config_entry.entry_id] = devices

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    api.subscribe()

    def update_published():
        """Handle a push update."""
        dispatcher_send(hass, PUSH_UPDATE)

    for _device in devices[ProductType.DELTA_MAX]:
        _device.set_update_callback(update_published)

    async def resubscribe(now):
        """Resubscribe to MQTT updates."""
        await hass.async_add_executor_job(api.unsubscribe)
        api.subscribe()

        # refresh even required?
        # await asyncio.sleep(60)
        # await api.refresh_devices()

    config_entry.async_on_unload(async_track_time_interval(hass, resubscribe, INTERVAL))

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    ):
        api: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][
            config_entry.entry_id
        ]
        api.disconnect()
        hass.data[DOMAIN][API_CLIENT].pop(config_entry.entry_id)
        hass.data[DOMAIN][DEVICES].pop(config_entry.entry_id)
        # hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class EcoFlowIotOpenEntity(Entity):
    """Define a base EcoFlow Iot Open entity."""

    _attr_should_poll = False

    def __init__(self, EcoFlowIotOpen: Device) -> None:
        """Initialize."""
        self._EcoFlowIotOpen = EcoFlowIotOpen
        self._attr_name = EcoFlowIotOpen.device_name
        self._attr_unique_id = (
            f"{EcoFlowIotOpen.serial_number}_{EcoFlowIotOpen.device_name}"
        )
        self._update_callback: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        """Subscribe to device events."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(self.hass, PUSH_UPDATE, self.on_update_received)
        )

    @callback
    def on_update_received(self) -> None:
        """Update was pushed from the ecoent API."""
        self.async_write_ha_state()

    # @cached_property
    # def available(self) -> bool:
    #     """Return if the device is online or not."""
    #     return self._EcoFlowIotOpen.online

    @cached_property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._EcoFlowIotOpen.serial_number)},
            manufacturer="EcoFlow",
            name=self._EcoFlowIotOpen.device_name,
            model=self._EcoFlowIotOpen.model,
        )

    def set_update_callback(self, update_callback: Callable[[], None]) -> None:
        """Set callback to run when state changes."""
        self._update_callback = update_callback
