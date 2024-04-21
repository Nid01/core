"""EcoFlow PowerStream."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfPower

from . import Device


class PowerStream(Device):
    """PowerStream."""

    def sensors(self) -> list[SensorEntityDescription]:
        """Available sensors for PowerStream."""
        return [
            SensorEntityDescription(
                key="iot.invOutputWatts",
                name="inv_Output_Watts",
                device_class=SensorDeviceClass.POWER,
                native_unit_of_measurement=UnitOfPower.WATT,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            SensorEntityDescription(
                key="iot.batSoc",
                name="battery_level_int",
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=PERCENTAGE,
                state_class=SensorStateClass.MEASUREMENT,
            ),
        ]

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "PowerStream"

    # @property
    # def inv_Output_Watts(self) -> Union[float, None]:
    #     """Return the value 0-600 or 0-800 of the inverter output watts."""

    #     inv_Output_Watts: float | None = self._device_info.get("iot.invOutputWatts")
    #     if inv_Output_Watts is None:
    #         return None
    #     return inv_Output_Watts * 0.1

    # @property
    # def battery_level(self) -> Union[int, None]:
    #     """Return the value 0-100? of the battery level."""
    #     return self._device_info.get("iot.batSoc")


# quota all response, via mqtt data will have addr = "iot" as prefix
# {
#     "20_1.acOffFlag": 1,
#     "20_1.antiBackFlowFlag": 6000,
#     "20_1.batErrCode": 0,
#     "20_1.batErrorInvLoadLimit": 8000,
#     "20_1.batInputCur": 0,
#     "20_1.batInputVolt": 541,
#     "20_1.batInputWatts": 650,
#     "20_1.batLoadLimitFlag": 0,
#     "20_1.batOffFlag": 0,
#     "20_1.batOpVolt": 570,
#     "20_1.batOutputLoadLimit": 6000,
#     "20_1.batSoc": 51,
#     "20_1.batStatue": 5,
#     "20_1.batSystem": 0,
#     "20_1.batTemp": 310,
#     "20_1.batWarningCode": 0,
#     "20_1.bmsReqChgAmp": 0,
#     "20_1.bmsReqChgVol": 581890,
#     "20_1.bpType": 2,
#     "20_1.chgRemainTime": 5999,
#     "20_1.consNum": 0,
#     "20_1.consWatt": 0,
#     "20_1.dsgRemainTime": 1657,
#     "20_1.dynamicWatts": 0,
#     "20_1.feedProtect": 1,
#     "20_1.floadLimitOut": 2640,
#     "20_1.geneNum": 1,
#     "20_1.geneWatt": 2694,
#     "20_1.gridConsWatts": 0,
#     "20_1.heartbeatFrequency": 2,
#     "20_1.installCountry": 17477,
#     "20_1.installTown": 0,
#     "20_1.interfaceConnFlag": 7,
#     "20_1.invBrightness": 306,
#     "20_1.invDemandWatts": 2690,
#     "20_1.invErrCode": 0,
#     "20_1.invFreq": 499,
#     "20_1.invInputVolt": 0,
#     "20_1.invLoadLimitFlag": 0,
#     "20_1.invOnOff": 1,
#     "20_1.invOpVolt": 2358,
#     "20_1.invOutputCur": 1219,
#     "20_1.invOutputLoadLimit": 6000,
#     "20_1.invOutputWatts": 2690,
#     "20_1.invRelayStatus": 17,
#     "20_1.invStatue": 6,
#     "20_1.invTemp": 0,
#     "20_1.invToOtherWatts": 2690,
#     "20_1.invToPlugWatts": 0,
#     "20_1.invWarnCode": 0,
#     "20_1.llcErrCode": 0,
#     "20_1.llcInputVolt": 0,
#     "20_1.llcOffFlag": 0,
#     "20_1.llcOpVolt": 4352,
#     "20_1.llcStatue": 3,
#     "20_1.llcTemp": 530,
#     "20_1.llcWarningCode": 0,
#     "20_1.lowerLimit": 10,
#     "20_1.meshId": 11245728,
#     "20_1.meshLayel": 1,
#     "20_1.mqttErr": 6,
#     "20_1.mqttErrTime": 1713103879,
#     "20_1.parentMac": 894154823,
#     "20_1.permanentWatts": 2690,
#     "20_1.plugTotalWatts": 0,
#     "20_1.pv1CtrlMpptOffFlag": 0,
#     "20_1.pv1ErrCode": 0,
#     "20_1.pv1InputCur": 42,
#     "20_1.pv1InputVolt": 292,
#     "20_1.pv1InputWatts": 1190,
#     "20_1.pv1OpVolt": 2916,
#     "20_1.pv1RelayStatus": 0,
#     "20_1.pv1Statue": 4,
#     "20_1.pv1Temp": 570,
#     "20_1.pv1WarnCode": 0,
#     "20_1.pv2CtrlMpptOffFlag": 0,
#     "20_1.pv2ErrCode": 0,
#     "20_1.pv2InputCur": 27,
#     "20_1.pv2InputVolt": 315,
#     "20_1.pv2InputWatts": 850,
#     "20_1.pv2OpVolt": 3184,
#     "20_1.pv2RelayStatus": 0,
#     "20_1.pv2Statue": 4,
#     "20_1.pv2Temp": 570,
#     "20_1.pv2WarningCode": 0,
#     "20_1.pvPowerLimitAcPower": 7746,
#     "20_1.pvToInvWatts": 2040,
#     "20_1.ratedPower": 6000,
#     "20_1.resetCount": 4343,
#     "20_1.resetReason": 3,
#     "20_1.selfMac": 870944968,
#     "20_1.spaceDemandWatts": 2690,
#     "20_1.staIpAddr": 838117568,
#     "20_1.supplyPriority": 0,
#     "20_1.updateTime": "2024-04-14 23:46:04",
#     "20_1.upperLimit": 100,
#     "20_1.uwloadLimitFlag": 5,
#     "20_1.uwlowLightFlag": 0,
#     "20_1.uwsocFlag": 0,
#     "20_1.wifiErr": 8,
#     "20_1.wifiErrTime": 1712776156,
#     "20_1.wifiRssi": -49,
#     "20_1.wirelessErrCode": 0,
#     "20_1.wirelessWarnCode": 0,
#     "20_134.task1": {
#       "taskIndex": 0,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task10": {
#       "taskIndex": 9,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task11": {
#       "taskIndex": 10,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task2": {
#       "taskIndex": 1,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task3": {
#       "taskIndex": 2,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task4": {
#       "taskIndex": 3,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task5": {
#       "taskIndex": 4,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task6": {
#       "taskIndex": 5,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task7": {
#       "taskIndex": 6,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task8": {
#       "taskIndex": 7,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.task9": {
#       "taskIndex": 8,
#       "timeRange": {
#         "isConfig": false,
#         "isEnable": false,
#         "startTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "stopTime": {
#           "day": 0,
#           "hour": 0,
#           "min": 0,
#           "month": 0,
#           "sec": 0,
#           "week": 0,
#           "year": 0
#         },
#         "timeData": 0,
#         "timeMode": 0
#       },
#       "type": 0
#     },
#     "20_134.updateTime": "2024-04-14 22:12:06"
#   }
