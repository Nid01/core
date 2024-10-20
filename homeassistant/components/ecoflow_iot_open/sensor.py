"""EcoFlow IoT Open sensor module."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import cached_property
import json
from typing import Any

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
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
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .api import EcoFlowIoTOpenAPIInterface
from .const import API_CLIENT, DOMAIN, PRODUCTS
from .entities import EcoFlowBaseEntity
from .products import BaseDevice, ProductType


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors based on a config entry."""

    api: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][
        config_entry.entry_id
    ]
    products: dict[ProductType, dict[str, BaseDevice]] = hass.data[DOMAIN][PRODUCTS][
        config_entry.entry_id
    ]

    sensors: list = []
    for devices in products.values():
        for device in devices.values():
            sensors.extend(device.sensors(api))

    if sensors:
        async_add_entities(sensors)


class BaseSensorEntity(SensorEntity, EcoFlowBaseEntity):
    """Base sensor entity."""

    _attr_should_poll = False

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize."""
        super().__init__(api, device, mqtt_key, title, enabled, auto_enable)
        if title != "":
            self.entity_id = f"{SENSOR_DOMAIN}.{device.device_name.replace(' ', '_').replace('-', '_').replace('.', '_')}_{title}"
        else:
            self.entity_id = f"{SENSOR_DOMAIN}.{device.device_name.replace(' ', '_').replace('-', '_').replace('.', '_')}_{mqtt_key}"

        # self.entity_description = description

        if mqtt_key in (
            "bmsMaster.cellTemp",
            "bmsMaster.cellVol",
            "bmsSlave1.cellTemp",
            "bmsSlave1.cellVol",
            "iot.batInputWatts",
            "iot.historyBatInputWatts",
            "kit.productInfoDetails",
            "iot.switchState",
        ):
            unique_id = f"{device.serial_number}_{mqtt_key}_{title.replace(' ', '_').replace('-', '_').replace('.', '_')}"
        else:
            unique_id = f"{device.serial_number}_{mqtt_key}"
        self._attr_unique_id = unique_id

    def _update_value(self, val: Any) -> bool:
        if self._attr_native_value != val:
            self._attr_native_value = val

            if hasattr(self, "icon"):
                del self.icon  # invalidate cached icon because doesn't update properly
            return True
        return False


class BatterySensorEntity(BaseSensorEntity):
    """Sensor for battery percentage level."""

    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
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

        super().__init__(api, device, mqtt_key, title, enabled, auto_enable)
        self._list_position = list_position
        self._mqtt_key2 = mqtt_key2

    def _update_value(self, val: Any) -> bool:
        if isinstance(self._list_position, int) and isinstance(self._mqtt_key2, str):
            return super()._update_value(val[self._list_position].get(self._mqtt_key2))
        return super()._update_value(val)


class BinaryStateSensorEntity(BaseSensorEntity):
    """Sensor for binary states on/off."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_value(self, val: Any) -> bool:
        if self.name == "pd.beepState":
            return super()._update_value("Off" if val else "On")
        if val & (1 << 0):
            return super()._update_value("On")
        return super()._update_value("Off")

    @cached_property
    def icon(self) -> str:
        """Icon for binary state in context of mqtt key."""
        if self._attr_name in ("beeper", "pd.beepState"):
            if self.state == "On":
                return "mdi:volume-high"
            return "mdi:volume-mute"
        if self._mqtt_key == "inv.fanState":
            if self.state == "On":
                return "mdi:fan"
            return "mdi:fan-off"
        if self.state == "on":
            return "mdi:toggle-switch-variant"
        return "mdi:toggle-switch-variant-off"


class BrightnessSensorEntity(BaseSensorEntity):
    """Sensor for brightness from a range 0-1023 converted to 0-100."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(
            round(max(0, min(100, (val - 0) / (1023 - 0) * (100 - 0) + 0)))
        )


class ChargingStateSensorEntity(BaseSensorEntity):
    """Sensor for battery charging state."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-charging"
    # _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def _update_value(self, val: Any) -> bool:
        if val == 0:
            return super()._update_value("charging")
        if val == 1:
            return super()._update_value("unused")
        if val == 2:
            return super()._update_value("discharging")
        return super()._update_value(val)


# TODO Merge CountSensorEntity and CyclesSensorEntity # pylint: disable=fixme
class CountSensorEntity(BaseSensorEntity):
    """Sensor for counter."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.TOTAL_INCREASING


class CurrentSensorEntity(BaseSensorEntity):
    """Sensor for ampere with different units."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device,
        key: str,
        unit=UnitOfElectricCurrent.AMPERE,
    ) -> None:
        """Initialize with unit for ampere and default to ampere."""
        self._api = api
        self.device = device
        self.key = key
        self._attr_native_unit_of_measurement = unit
        super().__init__(api, device, key)

    def _update_value(self, val: Any) -> bool:
        if self._attr_native_unit_of_measurement == UnitOfElectricCurrent.MILLIAMPERE:
            return super()._update_value(int(val))
        return super()._update_value(int(val) / 1000)


# TODO Merge CountSensorEntity and CyclesSensorEntity # pylint: disable=fixme
class CyclesSensorEntity(BaseSensorEntity):
    """Sensor for battery cycles."""

    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery-heart-variant"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING


class DegreeSensorEntity(BaseSensorEntity):
    """Sensor for angle."""

    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = DEGREE
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0
    _attr_icon = "mdi:format-text-rotation-angle-up"

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(float(val) + 10.0) if float(val) <= 75 else False


class DiagnosticSensorEntity(BaseSensorEntity):
    """Sensor for miscellaneous values."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    # 255

    def _update_value(self, val: Any) -> bool:
        if isinstance(val, dict):
            val_str = json.dumps(val)
            if len(val_str) > 255:
                return super()._update_value(val_str[:255])
            return super()._update_value(val)
        return super()._update_value(val)


class DurationSensorEntity(BaseSensorEntity):
    """Sensor for remaining minutes."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device,
        key: str,
        unit=UnitOfTime.MINUTES,
    ) -> None:
        """Initialize with unit for duration and default to minutes."""
        self._api = api
        self.device = device
        self.key = key
        self._attr_native_unit_of_measurement = unit
        super().__init__(api, device, key)


class EnergySensorEntity(BaseSensorEntity):
    """Sensor for energy."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def _update_value(self, val: Any) -> bool:
        ival = int(val)
        if ival > 0:
            return super()._update_value(ival / 1000)
        # TODO Reevaluate code and note why False should be returned, when ival is not above 0  # pylint: disable=fixme
        return False


class EnergyStorageSensorEntity(BaseSensorEntity):
    """Sensor for capacity."""

    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE
    _attr_native_unit_of_measurement = "Ah"  # "mAh"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / 1000)


class FrequencySensorEntity(BaseSensorEntity):
    """Sensor for frequency."""

    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        factor: float = 1,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize with factor, default is 1."""
        super().__init__(api, device, mqtt_key, title, enabled, auto_enable)
        self._factor = factor

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(int(val) / self._factor)


class IlluminanceSensorEntity(BaseSensorEntity):
    """Sensor for lux."""

    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ILLUMINANCE
    _attr_native_unit_of_measurement = LIGHT_LUX
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0

    @cached_property
    def icon(self) -> str:
        """Lux grade icon handling."""

        if isinstance(self.state, int):
            if self.state < 30000:
                return "mdi:brightness-5"
            if self.state < 80000:
                return "mdi:brightness-6"
            if self.state < 130000:
                return "mdi:brightness-4"
            if self.state >= 130000:
                return "mdi:brightness-7"
        return "mdi:brightness-5"


class IlluminanceGradeSensorEntity(BaseSensorEntity):
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


class ModeSensorEntity(BaseSensorEntity):
    """Sensor for mode."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def _update_value(self, val: Any) -> bool:
        if val == 0:
            return super()._update_value("Manual")
        if val == 1:
            return super()._update_value("Auto")
        return super()._update_value(val)


class ModeAsWordSensorEntity(BaseSensorEntity):
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


class PowerSensorEntity(BaseSensorEntity):
    """Sensor for watts."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = 0

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        factor: float = 1,
        value_filter: str | None = None,
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

        super().__init__(api, device, mqtt_key, title, enabled, auto_enable)
        self._factor = factor
        self._value_filter = value_filter
        self._list_position = list_position
        self._mqtt_key2 = mqtt_key2

    def _update_value(self, val: Any) -> bool:
        if isinstance(self._list_position, int) and isinstance(self._mqtt_key2, str):
            return super()._update_value(
                int(val[self._list_position].get(self._mqtt_key2)) * self._factor
            )
        if self._mqtt_key in ("iot.batInputWatts", "iot.historyBatInputWatts"):
            if (self._value_filter == "positive" and not val >= 0) or (
                self._value_filter == "negative" and not val <= 0
            ):
                return super()._update_value(0)
            return super()._update_value(abs(int(val)) * self._factor)

        return super()._update_value(int(val) * self._factor)


# class InPowerSensorEntity(PowerSensorEntity):
#     """Sensor for imported watts."""

#     _attr_icon = "mdi:transmission-tower-import"


# class OutPowerSensorEntity(PowerSensorEntity):
#     """Sensor for exported watts."""

#     _attr_icon = "mdi:transmission-tower-export"


# class InPowerSolarSensorEntity(InPowerSensorEntity):
#     """Sensor for watts imported from solar panels."""

#     _attr_icon = "mdi:solar-power"

#     def _update_value(self, val: Any) -> bool:
#         return super()._update_value(int(val) / 10)


# class OutPowerDcSensorEntity(PowerSensorEntity):
#     """Sensor for exported watts with direct current."""

#     _attr_icon = "mdi:transmission-tower-export"

#     def _update_value(self, val: Any) -> bool:
#         return super()._update_value(int(val) / 10)


class ProductInfoDetailSensorEntity(BaseSensorEntity):
    """Sensor for product info details."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        list_position: int,
        mqtt_key2: str,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize with list_position and additional dictionary key."""
        if title == "":
            title = "Port-" + str(list_position) + "-" + mqtt_key2

        if mqtt_key2 == "curPower":
            _attr_device_class = SensorDeviceClass.POWER
            _attr_native_unit_of_measurement = UnitOfPower.WATT
            _attr_state_class = SensorStateClass.MEASUREMENT
            # _attr_native_value = 0

        super().__init__(api, device, mqtt_key, title, enabled, auto_enable)
        self._list_position = list_position
        self._mqtt_key2 = mqtt_key2

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(val[self._list_position].get(self._mqtt_key2))


# TODO Merge ProtectionSensorEntities # pylint: disable=fixme
class ProtectionFromRainSensorEntity(BaseSensorEntity):
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


class ProtectionFromWindSensorEntity(BaseSensorEntity):
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


class StatusSensorEntity(BaseSensorEntity):
    """Sensor for device status."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    _attr_icon = "mdi:wifi"

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize with list_position and additional dictionary key."""

        super().__init__(api, device, mqtt_key, title, enabled, auto_enable)
        async_track_time_interval(
            self.hass,
            self._check_device_availability,
            timedelta(seconds=self._api.availability_check_interval_sec),
        )

    async def _check_device_availability(self, now):
        """Periodically check and update device availability."""
        if self.state == "online":
            if self.extra_state_attributes and self.extra_state_attributes.get(
                "last_updated"
            ):
                time_diff = now - self.extra_state_attributes["last_updated"]
                device_online = time_diff < timedelta(
                    seconds=self._api.availability_check_interval_sec * 4
                )
                if not device_online:
                    self._device.set_availability(device_online)
                    self.hass.bus.fire(
                        f"device_{self._device.serial_number}_availability", {}
                    )
                    super()._update_value("assume_offline")

    def _update_value(self, val: Any) -> bool:
        self._device.set_availability(val)
        self.hass.bus.fire(f"device_{self._device.serial_number}_availability", {})

        if super()._update_value("online" if val else "offline"):
            return True
        return False

    @cached_property
    def icon(self) -> str | None:
        """Device status icon handling."""

        if self.state == "online":
            return "mdi:wifi"
        if self.state == "assume_offline":
            return "mdi:wifi-alert"
        return "mdi:wifi-off"

    @cached_property
    def available(self) -> bool:
        """Returns the status sensor entity always as available."""
        return True


class TemperateSensorEntity(BaseSensorEntity):
    """Sensor for temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    # _attr_native_value = -1

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        factor: float = 1,
        list_position: int | None = None,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize with list_position, when passed on."""
        if isinstance(list_position, int) and title == "":
            title = mqtt_key + "-" + str(list_position).zfill(2)

        super().__init__(api, device, mqtt_key, title, enabled, auto_enable)
        self._list_position = list_position
        self._factor = factor

    def _update_value(self, val: Any) -> bool:
        if self._list_position is not None:
            try:
                value = val[self._list_position]
            except (IndexError, TypeError, ValueError):
                return False
        else:
            value = val
        if value < 10000:
            return super()._update_value(value * self._factor)
        # cellTemp-0, ellTemp-1, cellTemp-2, ... show unsually high values like 12374
        return super()._update_value(value / 1000 * self._factor)


class TimestampSensorEntity(BaseSensorEntity):
    """Sensor for timestamp."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def _update_value(self, val: Any) -> bool:
        return super()._update_value(datetime.fromtimestamp(val, UTC))


# class InMilliVoltSensorEntity(MilliVoltSensorEntity):
#     """Sensor for imported millivoltage."""

#     _attr_icon = "mdi:transmission-tower-import"
#     _attr_suggested_display_precision = 0


# class OutMilliVoltSensorEntity(MilliVoltSensorEntity):
#     """Sensor for exported millivoltage."""

#     _attr_icon = "mdi:transmission-tower-export"
#     _attr_suggested_display_precision = 0


class VoltageSensorEntity(BaseSensorEntity):
    """Sensor for voltage."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    # _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        api: EcoFlowIoTOpenAPIInterface,
        device: BaseDevice,
        mqtt_key: str,
        list_position: int | None = None,
        title: str = "",
        enabled: bool = True,
        auto_enable: bool = False,
    ) -> None:
        """Initialize with list_position, when passed on."""
        if isinstance(list_position, int) and title == "":
            title = mqtt_key + "-" + str(list_position).zfill(2)

        super().__init__(api, device, mqtt_key, title, enabled, auto_enable)
        self._list_position = list_position

    def _update_value(self, val: Any) -> bool:
        if self._list_position is not None:
            try:
                value = int(val[self._list_position]) / 1000
            except (IndexError, TypeError, ValueError):
                return False
        else:
            value = int(val) / 1000
        return super()._update_value(value)


class WaterSensorEntity(BaseSensorEntity):
    """Sensor for water registration."""

    _attr_icon = "mdi:weather-rainy"
    _attr_entity_category = EntityCategory.DIAGNOSTIC


class WindSensorEntity(BaseSensorEntity):
    """Sensor for wind registration."""

    _attr_icon = "mdi:weather-windy-variant"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
