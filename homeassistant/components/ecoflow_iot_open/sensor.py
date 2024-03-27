"""EcoFlow IoT Open sensor module."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DELTA_MAX, DEVICES, DOMAIN, EcoFlowDevice

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="battery_level",
        name="battery_level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor based on a config entry."""

    devices = hass.data[DOMAIN][DEVICES][entry.entry_id]
    # device = data[EcoFlowProductType.DELTA_MAX].copy()

    sensors: list = []
    # for device in devices:
    sensors.extend(
        BatterySensor(device, "bmsMaster.soc")
        for device in devices.values()
        if device.serial_number.startswith(DELTA_MAX)
    )

    if sensors:
        async_add_entities(sensors)

    # async def get_entities():
    #     """Get a list of entities."""
    #     device: DELTAMax = hass.data[DOMAIN][entry.entry_id]
    #     async_add_enttities(
    #         BaseSensorEntity(device, description)
    #         for desc
    #     )
    #     entities = []
    #     ecoFlowIoTOpenAPI: EcoFlowIoTOpenAPI = hass.data[DOMAIN][entry.entry_id]
    #     for device_dict in ecoFlowIoTOpenAPI.devices:
    #         entity_dicts = device_dict.get(CONF_ENTITIES, {}).get("sensor", [])
    #         entities += [BaseSensorEntity(**d) for d in entity_dicts]


class SensorBase(SensorEntity):
    """Representation of a EcoFlow IoT Open sensor."""

    _attr_should_poll = False

    def __init__(self, device: EcoFlowDevice) -> None:
        """Initizialize the sensor."""
        self._device = device
        # self.entity_description = description
        # self._attr_available = False
        # self._attr_unique_id = f"{device.serial_number}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._device.serial_number)}}

    @property
    def available(self) -> bool:
        """Return True if the device."""
        return self._device.device_info.get("online") == 1

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        self._device.register_callback  # pylint: disable=pointless-statement

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from HA."""
        self._device.remove_callback  # pylint: disable=pointless-statement


class BatterySensor(SensorBase):
    """Representation of a battery sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, device: EcoFlowDevice, key: str) -> None:
        """Initialize the battery sensor."""
        super().__init__(device)
        self._attr_unique_id = f"{device.serial_number}_battery"
        self._attr_state = device.device_info.get(key)

    # @property
    # def state(self) -> StateType:
    #     """Return the state of the sensor."""
    #     return self._attr_state
