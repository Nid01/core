"""EcoFlow PowerStream."""

from collections.abc import Sequence

from ..api import EcoFlowIoTOpenAPIInterface
from ..number import BaseNumberEntity, BatteryLevelEntity, BrightnessEntity, PowerEntity
from ..sensor import (
    BaseSensorEntity,
    BatterySensorEntity,
    CountSensorEntity,
    CurrentSensorEntity,
    DiagnosticSensorEntity,
    DurationSensorEntity,
    FrequencySensorEntity,
    PowerSensorEntity,
    TemperateSensorEntity,
    VoltageSensorEntity,
)
from ..switch import BaseSwitchEntity, PowerSupplyPriorityEntity
from . import BaseDevice


class PowerStream(BaseDevice):
    """PowerStream."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "PowerStream"

    def sensors(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[BaseSensorEntity]:
        """Available sensors for PowerStream."""

        device_info_keys = set(self._device_info.keys())
        device_info_keys.remove("deviceName")
        device_info_keys.remove("online")
        device_info_keys.remove("sn")

        battery_keys = [
            "iot.batSoc",
        ]

        battery_sensors = [
            BatterySensorEntity(api, self, key)
            for key in battery_keys
            if key in device_info_keys
        ]

        # brightness_keys = [
        #     "iot.invBrightness",
        # ]

        # brightness_sensors = [
        #     BrightnessSensorEntity(api, self, key)
        #     for key in brightness_keys
        #     if key in device_info_keys
        # ]

        count_keys = [
            "iot.resetCount",
        ]

        count_sensors = [
            CountSensorEntity(api, self, key)
            for key in count_keys
            if key in device_info_keys
        ]

        current_keys = [
            "iot.batInputCur",
            "iot.bmsReqChgAmp",
            "iot.invOutputCur",
            "iot.pv1InputCur",
            "iot.pv2InputCur",
        ]

        current_sensors = [
            CurrentSensorEntity(api, self, key)
            for key in current_keys
            if key in device_info_keys
        ]

        duration_keys = [
            "iot.chgRemainTime",
            "iot.dsgRemainTime",
        ]

        duration_sensors = [
            DurationSensorEntity(api, self, key)
            for key in duration_keys
            if key in device_info_keys
        ]

        frequency_keys = [
            "iot.invFreq",
        ]

        frequency_sensors = [
            FrequencySensorEntity(api, self, key, 10)
            for key in frequency_keys
            if key in device_info_keys
        ]

        power_keys = [
            "iot.acSetWatts",
            "iot.antiBackFlowFlag",
            "iot.batErrorInvLoadLimit",
            # "iot.batInputWatts",
            "iot.batOutputLoadLimit",
            "iot.consWatt",
            "iot.dynamicWatts",
            "iot.floadLimitOut",
            "iot.geneWatt",
            "iot.gridConsWatts",
            # "iot.historyBatInputWatts",
            "iot.historyGridConsWatts",
            "iot.historyInvOutputWatts",
            "iot.historyInvToPlugWatts",
            "iot.historyPermanentWatts",
            "iot.historyPlugTotalWatts",
            "iot.historyPvToInvWatts",
            "iot.invDemandWatts",
            "iot.invOutputLoadLimit",
            "iot.invOutputWatts",
            "iot.invToOtherWatts",
            "iot.invToPlugWatts",
            "iot.permanentWatts",
            "iot.plugTotalWatts",
            "iot.pv1InputWatts",
            "iot.pv2InputWatts",
            "iot.pvPowerLimitAcPower",
            "iot.pvToInvWatts",
            "iot.ratedPower",
            "iot.spaceDemandWatts",
        ]

        power_sensors = [
            PowerSensorEntity(
                api,
                self,
                key,
                0.1,
            )
            for key in power_keys
            if key in device_info_keys
        ]

        power_sensors.append(
            PowerSensorEntity(
                api,
                self,
                "iot.batInputWatts",
                0.1,
                value_filter="negative",
                title="iot.batInputWatts",
            )
        )

        power_sensors.append(
            PowerSensorEntity(
                api,
                self,
                "iot.batInputWatts",
                0.1,
                value_filter="positive",
                title="iot.batOutputWatts",
            )
        )

        power_sensors.append(
            PowerSensorEntity(
                api,
                self,
                "iot.historyBatInputWatts",
                0.1,
                value_filter="negative",
                title="iot.historyBatInputWatts",
            )
        )

        power_sensors.append(
            PowerSensorEntity(
                api,
                self,
                "iot.historyBatInputWatts",
                0.1,
                value_filter="positive",
                title="iot.historyBatOutputWatts",
            )
        )

        temperature_factors = {
            "iot.batTemp": 0.1,
            "iot.invTemp": 0.1,
            "iot.llcTemp": 0.1,
            "iot.pv1Temp": 0.1,
            "iot.pv2Temp": 0.1,
        }

        temperature_keys = [
            "iot.batTemp",
            "iot.espTempsensor",
            "iot.invTemp",
            "iot.llcTemp",
            "iot.pv1Temp",
            "iot.pv2Temp",
        ]

        temperature_sensors = [
            TemperateSensorEntity(
                api,
                self,
                key,
                temperature_factors.get(key, 1),
            )
            for key in temperature_keys
            if key in device_info_keys
        ]

        voltage_keys = [
            "iot.batInputVolt",
            "iot.batOpVolt",
            "iot.bmsReqChgVol",
            "iot.invInputVolt",
            "iot.invOpVolt",
            "iot.llcInputVolt",
            "iot.llcOpVolt",
            "iot.pv1InputVolt",
            "iot.pv1OpVolt",
            "iot.pv2InputVolt",
            "iot.pv2OpVolt",
        ]

        voltage_sensors = [
            VoltageSensorEntity(api, self, key)
            for key in voltage_keys
            if key in device_info_keys
        ]

        # milli_voltage_keys = [
        #     "iot.bmsReqChgVol",
        # ]

        # milli_voltage_sensors = [
        #     MilliVoltSensorEntity(dataHolder, self, key)
        #     for key in milli_voltage_keys
        #     if key in device_info_keys
        # ]

        ignored_keys = [
            "iot.2_1",
            "iot.2_2",
            "iot.batInputWatts",
            "iot.historyBatInputWatts",
            "iot.invBrightness",
            "iot.lowerLimit",
            "iot.mqttErrTime",  # Parse integer value as datetime?
            "iot.permanentWatts",
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
            "iot.updateTime",
            "iot.upperLimit",
            "iot.wifiErrTime",  # Parse integer value as datetime?
        ]

        found_keys = set(
            battery_keys
            + count_keys
            + current_keys
            + duration_keys
            + frequency_keys
            + ignored_keys
            + power_keys
            + temperature_keys
            + voltage_keys
        )

        diagnostic_keys = device_info_keys - found_keys

        diagnostic_sensors = [
            DiagnosticSensorEntity(api, self, key, enabled=False)
            for key in diagnostic_keys
        ]

        return [
            *battery_sensors,
            *count_sensors,
            *current_sensors,
            *duration_sensors,
            *diagnostic_sensors,
            *frequency_sensors,
            *power_sensors,
            *voltage_sensors,
            # StatusSensorEntity(api, self),
            *temperature_sensors,
        ]

    def switches(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[BaseSwitchEntity]:
        """Available switches for PowerStream."""

        return [
            PowerSupplyPriorityEntity(
                api,
                self,
                "iot.supplyPriority",
                command=lambda value: {
                    "cmdCode": "WN511_SET_SUPPLY_PRIORITY_PACK",
                    "params": {"supplyPriority": value},
                },
            ),
        ]

    def numbers(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[BaseNumberEntity]:
        """Available numbers for PowerStream."""

        return [
            PowerEntity(
                api,
                self,
                "iot.permanentWatts",
                min_value=0,
                max_value=800,
                command=lambda value: {
                    "cmdCode": "WN511_SET_PERMANENT_WATTS_PACK",
                    "params": {"permanentWatts": value * 10},
                },
            ),
            BatteryLevelEntity(
                api,
                self,
                "iot.lowerLimit",
                min_value=1,
                max_value=30,
                command=lambda value: {
                    "cmdCode": "WN511_SET_BAT_LOWER_PACK",
                    "params": {"lowerLimit": value},
                },
            ),
            BatteryLevelEntity(
                api,
                self,
                "iot.upperLimit",
                min_value=70,
                max_value=100,
                command=lambda value: {
                    "cmdCode": "WN511_SET_BAT_UPPER_PACK",
                    "params": {"upperLimit": value},
                },
            ),
            BrightnessEntity(
                api,
                self,
                "iot.invBrightness",
                min_value=0,
                max_value=100,
                command=lambda value: {
                    "cmdCode": "WN511_SET_BRIGHTNESS_PACK",
                    "params": {"brightness": round((value * 1023) / 100)},
                },
            ),
        ]

    # def datetimes(...)..
    # DateTimeEntity(dataHolder, self, "iot.updateTime"),
    # DateTimeEntity(dataHolder, self, "iot.wifiErrTime"), # Parse integer value as datetime?
    # MiscSensorEntity(dataHolder, self, "iot.mqttErrTime"), # Parse integer value as datetime?
