"""EcoFlow IoT Open sensor module."""

from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import EcoFlowIotOpenEntity
from .const import DOMAIN, PRODUCTS
from .products import Device, ProductType

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="battery_level",
        name="battery_level",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="inv_Output_Watts",
        name="inv_Output_Watts",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="watts",
        name="watts",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor based on a config entry."""

    products: dict[ProductType, dict[str, Device]] = hass.data[DOMAIN][PRODUCTS][
        entry.entry_id
    ]

    sensors: list = []
    for devices in products.values():
        for device in devices.values():
            sensors.extend(
                EcoFlowIoTOpenSensor(device, description)
                for description in SENSOR_TYPES
                if getattr(device, description.key, False) is not False
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
        value = getattr(self._device, self.entity_description.key)
        return value
