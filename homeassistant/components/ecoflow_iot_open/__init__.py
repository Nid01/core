"""The EcoFlow IoT Open integration."""

from __future__ import annotations  # noqa: I001

import logging


from homeassistant.components.blue_current import DATA


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


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up EcoFlow IoT Open from a config entry."""

    # TO DO 1. Create API instance
    # TO DO 2. Validate the API connection (and authentication)
    # TO DO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    # using components/econet as guideline

    accessKey = config_entry.data[CONF_ACCESS_KEY]
    secretKey = config_entry.data[CONF_SECRET_KEY]

    ecoFlowIoTOpenAPIConnector = EcoFlowIoTOpenAPI(hass, accessKey, secretKey)

    try:
        await hass.async_add_executor_job(ecoFlowIoTOpenAPIConnector.setup)
    except (InvalidCredentialsError, KeyError):
        _LOGGER.error("Invalid credentials provided")
        return False
    except EcoFlowIoTOpenError as err:
        _LOGGER.error("Config entry failed: %s", err)
        raise ConfigEntryNotReady from err

    # Do first update
    await hass.async_add_executor_job(ecoFlowIoTOpenAPIConnector.update_devices)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {DATA: ecoFlowIoTOpenAPIConnector}

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    ecoFlowIoTOpenAPIConnector.subscribe()

    # TO DO Setup MQTT client

    # hass.data[DOMAIN][entry.entry_id] = client

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
