"""EcoFlow DELTA Max."""

from typing import Union

from . import Device


class SingleAxisSolarTracker(Device):
    """Single Axis Solar Tracker."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "Single Axis Solar Tracker"

    @property
    def battery_level(self) -> Union[int, None]:
        """Return the value 0-100? of the battery level."""
        return self._device_info.get("iot.batteryPercent")


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
