"""EcoFlow Smart Plug."""

from collections.abc import Sequence

from homeassistant.components.sensor import SensorEntity

from ..api import EcoFlowIoTOpenDataHolder
from ..sensor import DiagnosticSensorEntity, PowerSensorEntity
from . import BaseDevice


class SmartPlug(BaseDevice):
    """Smart Plug."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "Smart Plug"

    def sensors(self, dataHolder: EcoFlowIoTOpenDataHolder) -> Sequence[SensorEntity]:
        """Available sensors for Smart Plug."""

        device_info_keys = set(self._device_info.keys())
        device_info_keys.remove("deviceName")
        device_info_keys.remove("online")
        device_info_keys.remove("sn")

        # "consNum": 1,
        # "consWatt": 0,
        # "country": 17477,
        # "current": 139,
        # "errCode": 0,
        # "freq": 50,
        # "geneNum": 1,
        # "geneWatt": 2989,
        # "heartbeatFrequency": 2,
        # "lanState": 4,
        # "matterFabric": 2,
        # "maxCur": 0,
        # "maxWatts": 2500,
        # "meshEnable": 0,
        # "meshId": 11245728,
        # "meshLayel": 1,
        # "mqttErr": 6,
        # "mqttErrTime": 1694016157,
        # "otaDlErr": 0,
        # "otaDlTlsErr": 0,
        # "parentMac": 0,
        # "parentWifiRssi": -45,
        # "resetCount": 8,
        # "resetReason": 1,
        # "rtcResetReason": 1,
        # "runTime": 431,
        # "selfEmsSwitch": 1,
        # "selfMac": 3401870404,
        # "staIpAddr": 821340352,
        # "stackFree": 66,
        # "stackMinFree": 37,
        # "switchSta": true,
        # "temp": 22,
        # "town": 0,
        # "updateTime": "2024-03-31 06:39:00",
        # "volt": 231,
        # "warnCode": 0,
        # "watts": 10,
        # "wifiErr": 8,
        # "wifiErrTime": 1710885604,

        ignored_keys = [
            "iot.watts",
            "iot.task1",
            "iot.task2",
            "iot.task3",
            "iot.task4",
            "iot.task5",
            "iot.task6",
            "iot.task7",
            "iot.task8",
            "iot.task9",
            "iot.task10",
            "iot.task11",
        ]

        found_keys = set(ignored_keys)

        diagnostic_keys = device_info_keys - found_keys

        diagnostic_sensors = [
            DiagnosticSensorEntity(dataHolder, self, key) for key in diagnostic_keys
        ]
        return [
            *diagnostic_sensors,
            PowerSensorEntity(
                dataHolder=dataHolder,
                device=self,
                mqtt_key="iot.watts",
                title="watts",
            ),
        ]
