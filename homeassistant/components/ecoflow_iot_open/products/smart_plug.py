"""EcoFlow Smart Plug."""

from typing import Union

from . import Device


class SmartPlug(Device):
    """Smart Plug."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "Smart Plug"

    @property
    def watts(self) -> Union[float, None]:
        """Return the integer value 0-2500 of the smart plug consumer watts."""

        watts: float | None = self._device_info.get("watts")
        if watts is None:
            return None
        return watts * 0.1


# quota all response without key prefix
# {
#   "brightness": 104,
#   "consNum": 1,
#   "consWatt": 0,
#   "country": 17477,
#   "current": 139,
#   "errCode": 0,
#   "freq": 50,
#   "geneNum": 1,
#   "geneWatt": 2989,
#   "heartbeatFrequency": 2,
#   "lanState": 4,
#   "matterFabric": 2,
#   "maxCur": 0,
#   "maxWatts": 2500,
#   "meshEnable": 0,
#   "meshId": 11245728,
#   "meshLayel": 1,
#   "mqttErr": 6,
#   "mqttErrTime": 1694016157,
#   "otaDlErr": 0,
#   "otaDlTlsErr": 0,
#   "parentMac": 0,
#   "parentWifiRssi": -45,
#   "resetCount": 8,
#   "resetReason": 1,
#   "rtcResetReason": 1,
#   "runTime": 431,
#   "selfEmsSwitch": 1,
#   "selfMac": 3401870404,
#   "staIpAddr": 821340352,
#   "stackFree": 66,
#   "stackMinFree": 37,
#   "switchSta": true,
#   "temp": 22,
#   "town": 0,
#   "updateTime": "2024-03-31 06:39:00",
#   "volt": 231,
#   "warnCode": 0,
#   "watts": 10,
#   "wifiErr": 8,
#   "wifiErrTime": 1710885604,
#   "task1": {
#     "taskIndex": 0,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task10": {
#     "taskIndex": 9,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task11": {
#     "taskIndex": 10,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task2": {
#     "taskIndex": 1,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task3": {
#     "taskIndex": 2,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task4": {
#     "taskIndex": 3,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task5": {
#     "taskIndex": 4,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task6": {
#     "taskIndex": 5,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task7": {
#     "taskIndex": 6,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task8": {
#     "taskIndex": 7,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "task9": {
#     "taskIndex": 8,
#     "timeRange": {
#       "isConfig": false,
#       "isEnable": false,
#       "startTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "stopTime": {
#         "day": 0,
#         "hour": 0,
#         "min": 0,
#         "month": 0,
#         "sec": 0,
#         "week": 0,
#         "year": 0
#       },
#       "timeData": 0,
#       "timeMode": 0
#     },
#     "type": 0
#   },
#   "updateTime": "2024-03-31 06:32:02"
# }
