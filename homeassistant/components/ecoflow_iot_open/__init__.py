"""The EcoFlow IoT Open integration."""

# from .products.powerstream import PowerStream
# from .products.single_axis_solar_tracker import SingleAxisSolarTracker
# from .products.smart_plug import SmartPlug
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

# from paho.mqtt import client as mqtt
from .data_holder import EcoFlowIoTOpenDataHolder
from .errors import (
    ClientError,
    EcoFlowIoTOpenError,
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
)

# from .products import BaseDevice


_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]
PUSH_UPDATE = "ecoflow_iot_open.push_update"

INTERVAL = timedelta(minutes=60)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up EcoFlow IoT Open from a config entry."""

    try:
        data_holder = EcoFlowIoTOpenDataHolder()
        api = await EcoFlowIoTOpenAPIInterface.certification(
            config_entry.data[CONF_ACCESS_KEY],
            config_entry.data[CONF_SECRET_KEY],
            config_entry.data[CONF_BASE_URL],
            data_holder,
        )
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
    hass.data[DOMAIN][DATA_HOLDER][config_entry.entry_id] = data_holder

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    await api.initializeDevices()

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
        api: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][
            config_entry.entry_id
        ]
        await api.disconnect()
        hass.data[DOMAIN][API_CLIENT].pop(config_entry.entry_id)
        hass.data[DOMAIN][PRODUCTS].pop(config_entry.entry_id)

    return unload_ok
