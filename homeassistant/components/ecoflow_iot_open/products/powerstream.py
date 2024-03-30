"""EcoFlow PowerStream."""

from typing import Union

from . import Device


class PowerStream(Device):
    """PowerStream."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "PowerStream"

    @property
    def inv_Output_Watts(self) -> Union[float, None]:
        """Return the value 0-600 or 0-800 of the inverter output watts."""

        inv_Output_Watts: float | None = self._device_info.get("invOutputWatts")
        if inv_Output_Watts is None:
            return None
        return inv_Output_Watts * 0.1

    @property
    def battery_level(self) -> Union[int, None]:
        """Return the value 0-100? of the battery level."""
        return self._device_info.get("batSoc")


# quota all response without key prefix
# {
#   "acOffFlag": 0,
#   "antiBackFlowFlag": 6000,
#   "batErrCode": 0,
#   "batErrorInvLoadLimit": 8000,
#   "batInputCur": 0,
#   "batInputVolt": 526,
#   "batInputWatts": 4200,
#   "batLoadLimitFlag": 0,
#   "batOffFlag": 0,
#   "batOpVolt": 620,
#   "batOutputLoadLimit": 6000,
#   "batSoc": 41,
#   "batStatue": 5,
#   "batSystem": 0,
#   "batTemp": 290,
#   "batWarningCode": 0,
#   "bmsReqChgAmp": 0,
#   "bmsReqChgVol": 569430,
#   "bpType": 2,
#   "chgRemainTime": 5999,
#   "consNum": 0,
#   "consWatt": 0,
#   "dsgRemainTime": 235,
#   "dynamicWatts": 0,
#   "feedProtect": 0,
#   "floadLimitOut": 4070,
#   "geneNum": 1,
#   "geneWatt": 4136,
#   "gridConsWatts": 0,
#   "heartbeatFrequency": 2,
#   "installCountry": 17477,
#   "installTown": 0,
#   "interfaceConnFlag": 3,
#   "invBrightness": 306,
#   "invDemandWatts": 4120,
#   "invErrCode": 0,
#   "invFreq": 501,
#   "invInputVolt": 0,
#   "invLoadLimitFlag": 0,
#   "invOnOff": 1,
#   "invOpVolt": 2349,
#   "invOutputCur": 17,
#   "invOutputLoadLimit": 6000,
#   "invOutputWatts": 4120,
#   "invRelayStatus": 2,
#   "invStatue": 6,
#   "invTemp": 0,
#   "invToOtherWatts": 4120,
#   "invToPlugWatts": 0,
#   "invWarnCode": 0,
#   "llcErrCode": 0,
#   "llcInputVolt": 620,
#   "llcOffFlag": 0,
#   "llcOpVolt": 3618,
#   "llcStatue": 3,
#   "llcTemp": 450,
#   "llcWarningCode": 0,
#   "lowerLimit": 15,
#   "meshId": 11245728,
#   "meshLayel": 1,
#   "mqttErr": 6,
#   "mqttErrTime": 1711821764,
#   "parentMac": 894154823,
#   "permanentWatts": 4120,
#   "plugTotalWatts": 0,
#   "pv1CtrlMpptOffFlag": 0,
#   "pv1ErrCode": 128,
#   "pv1InputCur": 0,
#   "pv1InputVolt": 0,
#   "pv1InputWatts": 0,
#   "pv1OpVolt": 0,
#   "pv1RelayStatus": 0,
#   "pv1Statue": 1,
#   "pv1Temp": 430,
#   "pv1WarnCode": 0,
#   "pv2CtrlMpptOffFlag": 0,
#   "pv2ErrCode": 128,
#   "pv2InputCur": 0,
#   "pv2InputVolt": 0,
#   "pv2InputWatts": 0,
#   "pv2OpVolt": 0,
#   "pv2RelayStatus": 0,
#   "pv2Statue": 1,
#   "pv2Temp": 430,
#   "pv2WarningCode": 0,
#   "pvPowerLimitAcPower": 6000,
#   "pvToInvWatts": 0,
#   "ratedPower": 6000,
#   "resetCount": 4290,
#   "resetReason": 1,
#   "selfMac": 870944968,
#   "spaceDemandWatts": 4120,
#   "staIpAddr": 838117568,
#   "supplyPriority": 0,
#   "updateTime": "2024-03-31 05:36:04",
#   "upperLimit": 100,
#   "uwloadLimitFlag": 5,
#   "uwlowLightFlag": 0,
#   "uwsocFlag": 0,
#   "wifiErr": 27,
#   "wifiErrTime": 1711343969,
#   "wifiRssi": -45,
#   "wirelessErrCode": 0,
#   "wirelessWarnCode": 0,
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
#   "updateTime": "2024-03-31 03:59:49"
# }
