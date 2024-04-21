"""EcoFlow IoT Open sensor module."""

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EcoFlowIotOpenEntity
from .api import EcoFlowIoTOpenAPIInterface
from .const import API_CLIENT, DOMAIN, PRODUCTS
from .products import Device, ProductType


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors based on a config entry."""

    client: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][entry.entry_id]
    products: dict[ProductType, dict[str, Device]] = hass.data[DOMAIN][PRODUCTS][
        entry.entry_id
    ]

    sensors: list = []
    for devices in products.values():
        for device in devices.values():
            sensors.extend(
                EcoFlowIoTOpenSensor(client, device, sensorEntityDescription)
                for sensorEntityDescription in device.sensors()
            )
            # sensors.extend(
            #     EcoFlowIoTOpenSensor(device, description)
            #     for description in SENSOR_TYPES
            #     if getattr(device, description.key, False) is not False
            # )

    if sensors:
        async_add_entities(sensors)


class EcoFlowIoTOpenSensor(EcoFlowIotOpenEntity, SensorEntity):
    """Define a EcoFLow sensor."""

    def __init__(
        self,
        client: EcoFlowIoTOpenAPIInterface,
        ecoflow_device: Device,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(client=client, device=ecoflow_device, mqtt_key=description.key)
        self.entity_description = description
        self._attr_name = f"{ecoflow_device.device_name}_{description.name}"
        self._attr_unique_id = f"{ecoflow_device.serial_number}_{description.name}"

    # @property
    # def native_value(self) -> StateType | date | datetime | Decimal | int:  # type: ignore
    #     """Return sensors state."""
    #     value = getattr(self._device, self.entity_description.key)
    #     return value
