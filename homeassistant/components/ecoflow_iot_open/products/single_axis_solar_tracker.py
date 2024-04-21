"""EcoFlow DELTA Max."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import LIGHT_LUX, PERCENTAGE

from . import Device


class SingleAxisSolarTracker(Device):
    """Single Axis Solar Tracker."""

    def sensors(self) -> list[SensorEntityDescription]:
        """Available sensors for Single Axis Solar Tracker."""
        return [
            SensorEntityDescription(
                key="iot.batteryPercent",
                name="battery_level_int",
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=PERCENTAGE,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            SensorEntityDescription(
                key="iot.lux",
                name="lux",
                device_class=SensorDeviceClass.ILLUMINANCE,
                native_unit_of_measurement=LIGHT_LUX,
                state_class=SensorStateClass.MEASUREMENT,
            ),
        ]

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "Single Axis Solar Tracker"

    # @property
    # def battery_level_int(self) -> Union[int, None]:
    #     """Return the value 0-100? of the battery level."""
    #     return self._device_info.get("iot.batteryPercent")

    # @property
    # def lux(self) -> Union[int, None]:
    #     """Return the lux value of the solar tracker."""
    #     return self._device_info.get("iot.lux")


# quota all response
# {
#     "iot.angle": 0,
#     "iot.angleManual": 4294967295,
#     "iot.angleTarget": 15,
#     "iot.batteryPercent": 92,
#     "iot.batteryTemperature": 20,
#     "iot.chargeState": 0,
#     "iot.chargeTimer": 1000,
#     "iot.errCode": 301,
#     "iot.lux": 0,
#     "iot.luxGrade": 0,
#     "iot.mode": 0,
#     "iot.scenes": 0,
#     "iot.shake": 0,
#     "iot.switchState": 36,
#     "iot.updateTime": "2024-03-31 02:16:44",
#     "iot.water": 0,
#     "iot.wind": 0,
#     "iot.word": 3
# }

# mqtt data
# {
#     "addr": "iot",
#     "cmdFunc": 32,
#     "cmdId": 1,
#     "param": {
#         "angle": 35,
#         "angleManual": 4294967295,
#         "angleTarget": 35,
#         "batteryPercent": 64,
#         "batteryTemperature": 32,
#         "chargeState": 1,
#         "chargeTimer": 1000,
#         "errCode": 3,
#         "lux": 45364,
#         "luxGrade": 1,
#         "mode": 0,
#         "scenes": 0,
#         "shake": 0,
#         "switchState": 52,
#         "water": 0,
#         "wind": 0,
#         "word": 4
#     }
# }
