"""EcoFlow IoT Open sensor module."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta
from functools import cached_property
import math
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    LIGHT_LUX,
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_STATUS_DATA_LAST_UPDATE,
    ATTR_STATUS_LAST_UPDATE,
    ATTR_STATUS_PHASE,
    ATTR_STATUS_RECONNECTS,
    ATTR_STATUS_SN,
    ATTR_STATUS_UPDATES,
    DOMAIN,
    PRODUCTS,
)
from .data_holder import EcoFlowIoTOpenDataHolder
from .products import BaseDevice, ProductType


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors based on a config entry."""

    # client: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][entry.entry_id]
    data_holder: EcoFlowIoTOpenDataHolder = hass.data[DOMAIN]["data_holder"][
        config_entry.entry_id
    ]
    products: dict[ProductType, dict[str, BaseDevice]] = hass.data[DOMAIN][PRODUCTS][
        config_entry.entry_id
    ]

    sensors: list = []
    for devices in products.values():
        for device in devices.values():
            sensors.extend(
                device.sensors(data_holder)
                # EcoFlowIoTOpenSensor(client, device, sensorEntityDescription)
                # for sensorEntityDescription in device.sensors()
            )
            # sensors.extend(
            #     EcoFlowIoTOpenSensor(device, description)
            #     for description in SENSOR_TYPES
            #     if getattr(device, description.key, False) is not False
            # )

    if sensors:
        async_add_entities(sensors)


class BaseSensorEntity(SensorEntity):
    """Define a base EcoFlow Iot Open entity."""

    _attr_should_poll = False

    def __init__(
        self,
        dataHolder: EcoFlowIoTOpenDataHolder,
        device: Any,  # dict[str, Any],
        mqtt_key: str,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize."""
        # self._attr_name = device.device_name
        # self._attr_name = title
        # self._attr_unique_id = f"{device.serial_number}_{device.device_name}"
        # self._attr_unique_id = self.gen_unique_id(device.serial_number, mqtt_key)

        # self.entity_description = description
        if title == "":
            title = mqtt_key

        self._attr_name = (
            f"{device.device_name} {title}"  # f"{device.device_name}_{mqtt_key}"
        )
        if mqtt_key in ("iot.switchState", "kit.productInfoDetails"):
            unique_id = f"{device.serial_number}_{mqtt_key}_{title.replace(' ', '_').replace('-', '_').replace('.', '_')}"
        else:
            unique_id = f"{device.serial_number}_{mqtt_key}"
        self._attr_unique_id = unique_id
        self._auto_enable = auto_enable
        self._attr_entity_registry_enabled_default = enabled
        self._dataHolder = dataHolder
        self._device = device
        self._mqtt_key = mqtt_key
        self._update_callback: Callable[[], None] | None = None
        self.__attributes_mapping: dict[str, str] = {}
        self.__attrs = OrderedDict[str, Any]()

    def attr(
        self, mqtt_key: str, title: str = "", default: Any = None
    ) -> BaseSensorEntity:
        """Add attribute to entity."""
        if title == "":
            title = mqtt_key
        self.__attributes_mapping[mqtt_key] = title
        self.__attrs[title] = default
        return self

    @staticmethod
    def gen_unique_id(sn: str, key: str):
        """Generate unique id for entity."""
        return "ecoflow-" + sn + "-" + key.replace(".", "-").replace("_", "-")

    async def async_added_to_hass(self) -> None:
        """Subscribe to device events."""
        await super().async_added_to_hass()
        disposableBase = self._dataHolder.params_observable().subscribe(self._updated)
        self.async_on_remove(disposableBase.dispose)

        # self.async_on_remove(
        #     async_dispatcher_connect(self.hass, PUSH_UPDATE, self.on_update_received)
        # )

    def _updated(self, data: dict[str, Any]):
        """Update attributes and values."""
        if data.get(self._device.serial_number):
            # update attributes
            for key, title in self.__attributes_mapping.items():
                if key in data:
                    self.__attrs[title] = data[key]

            # update value
            if self._mqtt_key in data[self._device.serial_number]:
                self._attr_available = True
                if self._auto_enable:
                    self._attr_entity_registry_enabled_default = True

                if self._update_value(data[self._device.serial_number][self._mqtt_key]):
                    self.schedule_update_ha_state()

    def _update_value(self, val: Any) -> bool:
        if self._attr_native_value != val:
            self._attr_native_value = val
            return True
        return False

    # def _update_value(self, val: Any) -> bool:
    #     return False

    @callback
    def on_update_received(self) -> None:
        """Update was pushed from the EcoFlow API."""
        self.schedule_update_ha_state()

    # @cached_property
    # def available(self) -> bool:
    #     """Return if the device is online or not."""
    #     return self._EcoFlowIotOpen.online

    @cached_property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.serial_number)},
            manufacturer="EcoFlow",
            name=self._device.device_name,
            model=self._device.model,
        )

    def set_update_callback(self, update_callback: Callable[[], None]) -> None:
        """Set callback to run when state changes."""
        self._update_callback = update_callback


class ChargingStateSensorEntity(BaseSensorEntity):
    """Sensor for battery charging state."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-charging"
    # _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def _update_value(self, val: Any) -> bool:
        if val == 0:
            return super()._update_value("unused")
        if val == 1:
            return super()._update_value("charging")
        if val == 2:
            return super()._update_value("discharging")
        return super()._update_value(val)


class CyclesSensorEntity(BaseSensorEntity):
    """Sensor for battery cycles."""

    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-heart-variant"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING


class CountSensorEntity(BaseSensorEntity):
    """Sensor for counter."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.TOTAL_INCREASING


class MiscSensorEntity(BaseSensorEntity):
    """Sensor for miscellaneous values."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC


class ModeSensorEntity(BaseSensorEntity):
    """Sensor for mode."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_value(self, val: Any) -> bool:
        if val == 0:
            return super()._update_value("Manual")
        if val == 1:
            return super()._update_value("Auto")
        return super()._update_value(val)


class ScenesSensorEntity(BaseSensorEntity):
    """Sensor for scene."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_value(self, val: Any) -> bool:
        if val == 0:
            return super()._update_value("Balcony")
        if val == 1:
            return super()._update_value("Courtyard")
        return super()._update_value(val)

    @cached_property
    def icon(self) -> str | None:
        """Scenes icon handling."""

        if self.state == "Balcony":
            return "mdi:format-text-rotation-angle-up"
        if self.state == "Courtyard":
            return "mdi:angle-acute"
        return None
        # return "mdi:eye"


class ModeWordSensorEntity(BaseSensorEntity):
    """Sensor for mode as word."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_value(self, val: Any) -> bool:
        if val == 3:
            return super()._update_value("Standby")
        if val == 4:
            return super()._update_value("Manual mode")
        if val == 5:
            return super()._update_value("Tracking sunlight")
        if val == 6:
            return super()._update_value("Detecting sunlight")
        if val == 7:
            return super()._update_value("Leveling out")
        return super()._update_value(val)


class BeeperSensorEntity(BaseSensorEntity):
    """Sensor for beeper."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_value(self, val: Any) -> bool:
        if val & (1 << 0):
            return super()._update_value("On")
        return super()._update_value("Off")

    @cached_property
    def icon(self) -> str:
        """Icon for beeper volume."""
        if self.state == "On":
            return "mdi:volume-high"
        return "mdi:volume-mute"


class RainProtectionSensorEntity(BaseSensorEntity):
    """Sensor for rain protection."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_value(self, val: Any) -> bool:
        if val & (1 << 1):
            return super()._update_value("On")
        return super()._update_value("Off")

    @cached_property
    def icon(self) -> str:
        """Icon for rain protection sensor."""
        if self.state == "On":
            return "mdi:umbrella-outline"
        return "mdi:umbrella-closed-variant"


class WaterSensorEntity(BaseSensorEntity):
    """Sensor for water registration."""

    _attr_icon = "mdi:weather-rainy"
    _attr_entity_category = EntityCategory.DIAGNOSTIC


class WindSensorEntity(BaseSensorEntity):
    """Sensor for wind registration."""

    _attr_icon = "mdi:weather-windy-variant"
    _attr_entity_category = EntityCategory.DIAGNOSTIC


class WindProtectionSensorEntity(BaseSensorEntity):
    """Sensor for wind protection."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_value(self, val: Any) -> bool:
        if val & (1 << 2):
            return super()._update_value("On")
        return super()._update_value("Off")

    @cached_property
    def icon(self) -> str:
        """Icon for wind protection sensor."""
        if self.state == "On":
            return "mdi:windsock"
        return "mdi:weather-windy"


class LevelSensorEntity(BaseSensorEntity):
    """Sensor for battery percentage level."""

    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        dataHolder: EcoFlowIoTOpenDataHolder,
        device: Any,
        mqtt_key: str,
        list_position: int | None = None,
        mqtt_key2: str | None = None,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize with list_position and additional dictionary key, when passed on."""
        if (
            isinstance(list_position, int)
            and isinstance(mqtt_key2, str)
            and title == ""
        ):
            title = str(list_position) + "-" + mqtt_key2

        super().__init__(dataHolder, device, mqtt_key, title, enabled, auto_enable)
        self._list_position = list_position
        self._mqtt_key2 = mqtt_key2

    def _update_value(self, val: Any) -> bool:
        if isinstance(self._list_position, int) and isinstance(self._mqtt_key2, str):
            return super()._update_value(val[self._list_position].get(self._mqtt_key2))
        return super()._update_value(val)


class SecondsRemainSensorEntity(BaseSensorEntity):
    """Sensor for remaining seconds."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0

    def _update_value(self, val: Any) -> Any:
        ival = int(val)
        if ival < 0 or ival > 5000:
            ival = 0

        return super()._update_value(ival)


class TempSensorEntity(BaseSensorEntity):
    """Sensor for temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = -1

    def __init__(
        self,
        dataHolder: EcoFlowIoTOpenDataHolder,
        device: Any,
        mqtt_key: str,
        factor: int = 1,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize with factor three-digit values from PowerStream."""
        super().__init__(dataHolder, device, mqtt_key, title, enabled, auto_enable)
        self.factor = factor

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / self.factor)


class RemainingTimeSensorEntity(BaseSensorEntity):
    """Sensor for remaining minutes."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0


class UsedTimeSensorEntity(BaseSensorEntity):
    """Sensor for used minutes."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0


class VoltSensorEntity(BaseSensorEntity):
    """Sensor for voltage."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 1000)


class MilliVoltSensorEntity(BaseSensorEntity):
    """Sensor for millivoltage."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    # _attr_suggested_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0


class InMilliVoltSensorEntity(MilliVoltSensorEntity):
    """Sensor for imported millivoltage."""

    _attr_icon = "mdi:transmission-tower-import"
    _attr_suggested_display_precision = 0


class OutMilliVoltSensorEntity(MilliVoltSensorEntity):
    """Sensor for exported millivoltage."""

    _attr_icon = "mdi:transmission-tower-export"
    _attr_suggested_display_precision = 0


class MilliAmpSensorEntity(BaseSensorEntity):
    """Sensor for milliampere."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.MILLIAMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0


class AmpSensorEntity(BaseSensorEntity):
    """Sensor for ampere."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 1000)


class WattsSensorEntity(BaseSensorEntity):
    """Sensor for watts."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0

    def __init__(
        self,
        dataHolder: EcoFlowIoTOpenDataHolder,
        device: Any,
        mqtt_key: str,
        list_position: int | None = None,
        mqtt_key2: str | None = None,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize with list_position and additional dictionary key, when passed on."""
        if (
            isinstance(list_position, int)
            and isinstance(mqtt_key2, str)
            and title == ""
        ):
            title = str(list_position) + "-" + mqtt_key2

        super().__init__(dataHolder, device, mqtt_key, title, enabled, auto_enable)
        self._list_position = list_position
        self._mqtt_key2 = mqtt_key2

    def _update_value(self, val: Any) -> bool:
        if isinstance(self._list_position, int) and isinstance(self._mqtt_key2, str):
            return super()._update_value(val[self._list_position].get(self._mqtt_key2))
        return super()._update_value(val)


class CapacitySensorEntity(BaseSensorEntity):
    """Sensor for capacity."""

    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE
    _attr_native_unit_of_measurement = "mAh"
    _attr_state_class = SensorStateClass.MEASUREMENT


class DeciwattSensorEntity(WattsSensorEntity):
    """Sensor for deciwatts."""

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class InWattsSensorEntity(WattsSensorEntity):
    """Sensor for imported watts."""

    _attr_icon = "mdi:transmission-tower-import"


class OutWattsSensorEntity(WattsSensorEntity):
    """Sensor for exported watts."""

    _attr_icon = "mdi:transmission-tower-export"


class InWattsSolarSensorEntity(InWattsSensorEntity):
    """Sensor for watts imported from solar panels."""

    _attr_icon = "mdi:solar-power"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class OutWattsDcSensorEntity(WattsSensorEntity):
    """Sensor for exported watts with direct current."""

    _attr_icon = "mdi:transmission-tower-export"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class LuxSensorEntity(BaseSensorEntity):
    """Sensor for lux."""

    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ILLUMINANCE
    _attr_native_unit_of_measurement = LIGHT_LUX
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0

    @cached_property
    def icon(self) -> str:
        """Lux grade icon handling."""

        if self.state < 30000:
            return "mdi:brightness-5"
        if self.state < 80000:
            return "mdi:brightness-6"
        if self.state < 130000:
            return "mdi:brightness-4"
        if self.state >= 130000:
            return "mdi:brightness-7"
        return "mdi:brightness-5"


class LuxGradeSensorEntity(BaseSensorEntity):
    """Sensor for lux grade."""

    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:brightness-4"

    def _update_value(self, val: Any) -> bool:
        if val == 0:
            return super()._update_value("poor")
        if val == 1:
            return super()._update_value("weak")
        if val == 2:
            return super()._update_value("strong")
        if val == 3:
            return super()._update_value("very strong")
        return super()._update_value(val)

    @cached_property
    def icon(self) -> str:
        """Lux grade icon handling."""

        if self.state in (0, "poor"):
            return "mdi:brightness-5"
        if self.state in (1, "weak"):
            return "mdi:brightness-6"
        if self.state in (2, "strong"):
            return "mdi:brightness-4"
        if self.state in (3, "very strong"):
            return "mdi:brightness-7"
        return "mdi:brightness-5"


class AngleSensorEntity(BaseSensorEntity):
    """Sensor for angle."""

    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = DEGREE
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0
    _attr_icon = "mdi:format-text-rotation-angle-up"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(float(val) + 10.0) if float(val) <= 75 else False


class FrequencySensorEntity(BaseSensorEntity):
    """Sensor for frequency."""

    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_state_class = SensorStateClass.MEASUREMENT

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 10)


class ProductInfoDetailsSensorEntity(BaseSensorEntity):
    """Sensor for product info details."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        dataHolder: EcoFlowIoTOpenDataHolder,
        device: Any,
        mqtt_key: str,
        list_position: int,
        mqtt_key2: str,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize with list_position and additional dictionary key."""
        if title == "":
            title = str(list_position) + "-" + mqtt_key2

        if mqtt_key2 == "curPower":
            _attr_device_class = SensorDeviceClass.POWER
            _attr_native_unit_of_measurement = UnitOfPower.WATT
            _attr_state_class = SensorStateClass.MEASUREMENT
            # _attr_native_value = 0

        super().__init__(dataHolder, device, mqtt_key, title, enabled, auto_enable)
        self._list_position = list_position
        self._mqtt_key2 = mqtt_key2

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(val[self._list_position].get(self._mqtt_key2))


class BrightnessSensorEntity(BaseSensorEntity):
    """Sensor for brightness from a range 0-1023 converted to 0-100."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(
            round(max(0, min(100, (val - 0) / (1023 - 0) * (100 - 0) + 0)))
        )


class StatusSensorEntity(BaseSensorEntity):
    """Sensor for status."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    DEADLINE_PHASE = 10
    CHECK_PHASES = [2, 4, 6]
    CONNECT_PHASES = [3, 5, 7]

    def __init__(
        self, dataHolder: EcoFlowIoTOpenDataHolder, device: Any, check_interval_sec=30
    ) -> None:
        """Initialize status sensor."""
        super().__init__(dataHolder, device, "Status")
        self._online = 0
        self._check_interval_sec = check_interval_sec
        self._attrs = OrderedDict[str, Any]()
        self._attrs[ATTR_STATUS_SN] = device.serial_number
        self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = self._dataHolder.params_time()
        self._attrs[ATTR_STATUS_UPDATES] = 0
        self._attrs[ATTR_STATUS_LAST_UPDATE] = None
        self._attrs[ATTR_STATUS_RECONNECTS] = 0
        self._attrs[ATTR_STATUS_PHASE] = 0

    async def async_added_to_hass(self) -> None:
        """Subscribe to device events."""
        await super().async_added_to_hass()

        # disposableBase = self._dataHolder.params_observable().subscribe(self._updated)
        params_d = self._dataHolder.params_observable().subscribe(self._updated)
        self.async_on_remove(params_d.dispose)

        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self.__check_status,
                timedelta(seconds=self._check_interval_sec),
            )
        )

        self._update_status(
            (dt_util.utcnow() - self._dataHolder.params_time()).total_seconds()
        )

    def __check_status(self, now: datetime):
        data_outdated_sec = (now - self._dataHolder.params_time()).total_seconds()
        phase = math.ceil(data_outdated_sec / self._check_interval_sec)
        self._attrs[ATTR_STATUS_PHASE] = phase
        time_to_reconnect = phase in self.CONNECT_PHASES
        time_to_check_status = phase in self.CHECK_PHASES

        if self._online == 1:
            if time_to_check_status or phase >= self.DEADLINE_PHASE:
                # online and outdated - refresh status to detect if device went offline
                self._update_status(data_outdated_sec)
            elif time_to_reconnect:
                # online, updated and outdated - reconnect
                self._attrs[ATTR_STATUS_RECONNECTS] = (
                    self._attrs[ATTR_STATUS_RECONNECTS] + 1
                )
                # not required due to use of aiomqtt?
                # self._client.reconnect()
                self.schedule_update_ha_state()

        # not required due to use of aiomqtt?
        # elif (
        #     not self._client.is_connected()
        # ):  # validate connection even for offline device
        #     self._attrs[ATTR_STATUS_RECONNECTS] = (
        #         self._attrs[ATTR_STATUS_RECONNECTS] + 1
        #     )
        #     #self._client.reconnect()
        #     self.schedule_update_ha_state()

    def _updated(self, data: dict[str, Any]):
        self._attrs[ATTR_STATUS_DATA_LAST_UPDATE] = self._dataHolder.params_time()
        if self._online == 0:
            self._update_status(0)

        self.schedule_update_ha_state()

    def _update_status(self, data_outdated_sec):
        if data_outdated_sec > self._check_interval_sec * self.DEADLINE_PHASE:
            self._online = 0
            self._attr_native_value = "assume_offline"
        else:
            self._online = 1
            self._attr_native_value = "assume_online"

        self._attrs[ATTR_STATUS_LAST_UPDATE] = dt_util.utcnow()
        self._attrs[ATTR_STATUS_UPDATES] = self._attrs[ATTR_STATUS_UPDATES] + 1
        self.schedule_update_ha_state()

    @cached_property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return the device-specific state attributes."""
        return self._attrs


# class EcoFlowIoTOpenSensor(BaseSensorEntity, SensorEntity):
#     """Define a EcoFLow sensor."""

#     def __init__(
#         self,
#         client: EcoFlowIoTOpenAPIInterface,
#         ecoflow_device: BaseDevice,
#         description: SensorEntityDescription,
#     ) -> None:
#         """Initialize."""
#         super().__init__(client=client, device=ecoflow_device, mqtt_key=description.key)
#         self.entity_description = description
#         self._attr_name = f"{ecoflow_device.device_name}_{description.name}"
#         self._attr_unique_id = f"{ecoflow_device.serial_number}_{description.name}"

# @property
# def native_value(self) -> StateType | date | datetime | Decimal | int:
#     """Return sensors state."""
#     value = getattr(self._device, self.entity_description.key)
#     return value
