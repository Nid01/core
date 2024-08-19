"""The EcoFlow IoT Open integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.dispatcher import dispatcher_send

from .api import EcoFlowIoTOpenAPIInterface
from .const import (
    API_CLIENT,
    CONF_ACCESS_KEY,
    CONF_BASE_URL,
    CONF_SECRET_KEY,
    DATA_HOLDER,
    DOMAIN,
    PRODUCTS,
    ProductType,
)
from .errors import (
    ClientError,
    EcoFlowIoTOpenError,
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]
PUSH_UPDATE = "ecoflow_iot_open.push_update"

INTERVAL = timedelta(minutes=60)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up EcoFlow IoT Open from a config entry."""

    try:
        api = EcoFlowIoTOpenAPIInterface(
            hass,
            config_entry.data[CONF_ACCESS_KEY],
            config_entry.data[CONF_SECRET_KEY],
            config_entry.data[CONF_BASE_URL],
        )
        await api.certification()
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

    hass.data.setdefault(DOMAIN, {API_CLIENT: {}, PRODUCTS: {}, DATA_HOLDER: {}})
    hass.data[DOMAIN][API_CLIENT][config_entry.entry_id] = api
    hass.data[DOMAIN][PRODUCTS][config_entry.entry_id] = products

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    await api.initializeDevices()

    await api.connect(hass, config_entry)

    def update_published():
        """Handle a push update."""
        dispatcher_send(hass, PUSH_UPDATE)

    for devices in products.values():
        for device in devices.values():
            device.set_update_callback(update_published)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    ):
        api: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][
            config_entry.entry_id
        ]
        await api.disconnect()
        hass.data[DOMAIN][API_CLIENT].pop(config_entry.entry_id)
        hass.data[DOMAIN][PRODUCTS].pop(config_entry.entry_id)

    return unload_ok
