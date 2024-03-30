"""EcoFlow IoT Open sensor module."""

from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import EcoFlowIotOpenEntity
from .const import DEVICES, DOMAIN
from .devices import Device, ProductType

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

    data = hass.data[DOMAIN][DEVICES][entry.entry_id]
    devices = data[ProductType.DELTA_MAX].copy()

    sensors: list = []
    sensors.extend(
        EcoFlowIoTOpenSensor(_device, description)
        for _device in devices
        for description in SENSOR_TYPES
        if getattr(_device, description.key, False) is not False
    )

    if sensors:
        async_add_entities(sensors)


class EcoFlowIoTOpenSensor(EcoFlowIotOpenEntity, SensorEntity):
    """Define a EcoFLow sensor."""

    def __init__(
        self, ecoflow_device: Device, description: SensorEntityDescription
    ) -> None:
        """Initialize."""
        super().__init__(ecoflow_device)
        self.entity_description = description
        self._attr_name = f"{ecoflow_device.device_name}_{description.name}"
        self._attr_unique_id = f"{ecoflow_device.serial_number}_{description.name}"

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return sensors state."""
        value = getattr(self._EcoFlowIotOpen, self.entity_description.key)
        return value
