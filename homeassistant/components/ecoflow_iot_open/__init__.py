"""The EcoFlow IoT Open integration."""

from __future__ import annotations  # noqa: I001

import logging


from .errors import (
    EcoFlowIoTOpenError,
    InvalidCredentialsError,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_ACCESS_KEY,
    CONF_SECRET_KEY,
    DOMAIN,
)
from .api import EcoFlowIoTOpenAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

Any = object()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EcoFlow IoT Open from a config entry."""

    # TO DO 1. Create API instance
    # TO DO 2. Validate the API connection (and authentication)
    # TO DO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    # using components/econet as guideline

    accessKey = entry.data[CONF_ACCESS_KEY]
    secretKey = entry.data[CONF_SECRET_KEY]

    try:
        api = await EcoFlowIoTOpenAPI.login(accessKey, secretKey)
    except InvalidCredentialsError:
        _LOGGER.error("Invalid credentials provided")
        return False
    except EcoFlowIoTOpenError as err:
        _LOGGER.error("Config entry failed: %s", err)
        raise ConfigEntryNotReady from err

    _LOGGER.debug(api.certificateAccount)
    # try:
    #     equipment = await api.get_devices_by_model(
    #         [
    #             EcoFlowModel.DELTA_MAX,
    #             EcoFlowModel.DELTA_MAX,
    #             EcoFlowModel.DELTA_MAX_SMART_EXTRA_BATTERY,
    #             EcoFlowModel.POWERSTREAM,
    #             EcoFlowModel.SMART_PLUG,
    #             EcoFlowModel.SINGLE_AXIS_SOLAR_TRACKER,
    #         ]
    #     )
    # except (ClientError, GenericHTTPError, InvalidResponseFormat) as err:
    #     raise ConfigEntryNotReady from err

    # hass.data.setdefault(DOMAIN, {})
    # is the upper call doing the same as the if condition below?
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # TO DO Setup MQTT client

    # hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
