"""EcoFlow PowerStream."""

from collections.abc import Sequence

from homeassistant.components.sensor import SensorEntity

from ..api import EcoFlowIoTOpenDataHolder
from ..sensor import (
    AmpSensorEntity,
    BrightnessSensorEntity,
    CountSensorEntity,
    DeciwattSensorEntity,
    FrequencySensorEntity,
    LevelSensorEntity,
    MiscSensorEntity,
    RemainingTimeSensorEntity,
    StatusSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)
from . import BaseDevice


class PowerStream(BaseDevice):
    """PowerStream."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "PowerStream"

    def sensors(self, dataHolder: EcoFlowIoTOpenDataHolder) -> Sequence[SensorEntity]:
        """Available sensors for PowerStream."""

        device_info_keys = set(self._device_info.keys())

        count_keys = [
            "iot.resetCount",
        ]

        count_sensors = [
            CountSensorEntity(dataHolder, self, key)
            for key in count_keys
            if key in device_info_keys
        ]

        deciwatt_keys = [
            "iot.acSetWatts",
            "iot.antiBackFlowFlag",
            "iot.batErrorInvLoadLimit",
            "iot.batInputWatts",
            "iot.batOutputLoadLimit",
            "iot.consWatt",
            "iot.dynamicWatts",
            "iot.floadLimitOut",
            "iot.geneWatt",
            "iot.gridConsWatts",
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

        deciwatt_sensors = [
            DeciwattSensorEntity(dataHolder, self, key)
            for key in deciwatt_keys
            if key in device_info_keys
        ]

        level_keys = [
            "iot.batSoc",
            "Iot.lowerLimit",
            "Iot.upperLimit",
        ]

        level_sensors = [
            LevelSensorEntity(dataHolder, self, key)
            for key in level_keys
            if key in device_info_keys
        ]

        amp_keys = [
            "iot.batInputCur",
            "iot.bmsReqChgAmp",
            "iot.invOutputCur",
            "iot.pv1InputCur",
            "iot.pv2InputCur",
        ]

        amp_sensors = [
            AmpSensorEntity(dataHolder, self, key)
            for key in amp_keys
            if key in device_info_keys
        ]

        frequency_keys = [
            "iot.invFreq",
        ]

        frequency_sensors = [
            FrequencySensorEntity(dataHolder, self, key)
            for key in frequency_keys
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
            VoltSensorEntity(dataHolder, self, key)
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

        brightness_keys = [
            "iot.invBrightness",
        ]

        brightness_sensors = [
            BrightnessSensorEntity(dataHolder, self, key)
            for key in brightness_keys
            if key in device_info_keys
        ]

        temp_keys = [
            "iot.batTemp",
            "iot.invTemp",
            "iot.llcTemp",
            "iot.pv1Temp",
            "iot.pv2Temp",
        ]

        temp_sensors = [
            TempSensorEntity(dataHolder, self, key, factor=10)
            for key in temp_keys
            if key in device_info_keys
        ]

        remaining_time_keys = [
            "iot.chgRemainTime",
            "iot.dsgRemainTime",
        ]

        remaining_time_sensors = [
            RemainingTimeSensorEntity(dataHolder, self, key)
            for key in remaining_time_keys
            if key in device_info_keys
        ]

        ignored_keys = [
            "iot.updateTime",
            "iot.wifiErrTime",  # Parse integer value as datetime?
            "iot.mqttErrTime",  # Parse integer value as datetime?
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
            "iot.2_1",
            "iot.2_2",
            "deviceName",
            "online",
            "sn",
        ]

        found_keys = set(
            count_keys
            + deciwatt_keys
            + level_keys
            + amp_keys
            + frequency_keys
            + voltage_keys
            # + milli_voltage_keys
            + brightness_keys
            + temp_keys
            + remaining_time_keys
            + ignored_keys
        )
        remaining_keys = device_info_keys - found_keys

        misc_sensors = [
            MiscSensorEntity(dataHolder, self, key) for key in remaining_keys
        ]

        return (
            count_sensors
            + deciwatt_sensors
            + level_sensors
            + amp_sensors
            + frequency_sensors
            + voltage_sensors
            # + milli_voltage_sensors
            + brightness_sensors
            + temp_sensors
            + remaining_time_sensors
            + misc_sensors
            + [StatusSensorEntity(dataHolder, self)]
        )

    # def datetimes(...)..
    # DateTimeEntity(dataHolder, self, "iot.updateTime"),
    # DateTimeEntity(dataHolder, self, "iot.wifiErrTime"), # Parse integer value as datetime?
    # MiscSensorEntity(dataHolder, self, "iot.mqttErrTime"), # Parse integer value as datetime?
