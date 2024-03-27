"""The EcoFlow IoT Open integration."""

from __future__ import annotations  # noqa: I001

from collections.abc import Callable
import logging


from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity


from .errors import (
    EcoFlowIoTOpenError,
    InvalidCredentialsError,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send

from .const import (
    API_CLIENT,
    CONF_ACCESS_KEY,
    CONF_SECRET_KEY,
    DOMAIN,
    DEVICES,
)
from .api import EcoFlowIoTOpenAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]
PUSH_UPDATE = "ecoflow_iot_open.push_update"

# Any = object()


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up EcoFlow IoT Open from a config entry."""

    accessKey = config_entry.data[CONF_ACCESS_KEY]
    secretKey = config_entry.data[CONF_SECRET_KEY]

    ecoFlowIoTOpenAPIConnector = EcoFlowIoTOpenAPI(hass, accessKey, secretKey)

    try:
        await ecoFlowIoTOpenAPIConnector.setup()
    except (InvalidCredentialsError, KeyError):
        _LOGGER.error("Invalid credentials provided")
        return False
    except EcoFlowIoTOpenError as err:
        _LOGGER.exception("Config entry failed: %s", err)
        raise ConfigEntryNotReady from err

    # Do first update
    await ecoFlowIoTOpenAPIConnector.update_devices()

    hass.data.setdefault(DOMAIN, {API_CLIENT: {}, DEVICES: {}})
    hass.data[DOMAIN][API_CLIENT][config_entry.entry_id] = ecoFlowIoTOpenAPIConnector
    hass.data[DOMAIN][DEVICES][
        config_entry.entry_id
    ] = ecoFlowIoTOpenAPIConnector.devices

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    ecoFlowIoTOpenAPIConnector.subscribe()

    def update_published():
        """Handle a push update."""
        dispatcher_send(hass, PUSH_UPDATE)

    for (
        _device
    ) in ecoFlowIoTOpenAPIConnector.devices.values():  # [EcoFlowProductType.DELTA_MAX]:
        _device.set_update_callback(update_published)
        break

    # async def resubscribe(now):
    #     """Resubscribe to MQTT updates."""
    #     await hass.async_add_executor_job(ecoFlowIoTOpenAPIConnector.unsubscribe)
    #     ecoFlowIoTOpenAPIConnector.subscribe()

    #     # Refresh values
    #     await asyncio.sleep(60)
    #     await ecoFlowIoTOpenAPIConnector.refresh_devices()

    # TODO Setup MQTT client # pylint: disable=fixme

    # hass.data[DOMAIN][entry.entry_id] = client

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class EcoFlowIotOpenEntity(Entity):
    """Define a base EcoFlow Iot Open entity."""

    _attr_should_poll = False

    def __init__(self, EcoFlowIotOpen) -> None:
        """Initialize."""
        self._EcoFlowIotOpen = EcoFlowIotOpen
        self._attr_name = EcoFlowIotOpen.device_name
        self._attr_unique_id = (
            f"{EcoFlowIotOpen.device_id}_{EcoFlowIotOpen.device_name}"
        )
        self._update_callback: Callable[[], None] | None = None

    async def async_added_to_hass(self):
        """Subscribe to device events."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(self.hass, PUSH_UPDATE, self.on_update_received)
        )

    @callback
    def on_update_received(self):
        """Update was pushed from the ecoent API."""
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if the device is online or not."""
        return self._EcoFlowIotOpen.connected

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._EcoFlowIotOpen.device_id)},
            manufacturer="Rheem",
            name=self._EcoFlowIotOpen.device_name,
        )

    def set_update_callback(self, update_callback: Callable[[], None]) -> None:
        """Set callback to run when state changes."""
        self._update_callback = update_callback
