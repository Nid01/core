"""EcoFlow Smart Plug."""

from collections.abc import Sequence

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfTime

from ..api import EcoFlowIoTOpenAPIInterface
from ..number import BrightnessEntity
from ..sensor import (
    CountSensorEntity,
    CurrentSensorEntity,
    DiagnosticSensorEntity,
    DurationSensorEntity,
    FrequencySensorEntity,
    PowerSensorEntity,
    TemperateSensorEntity,
    VoltageSensorEntity,
)
from ..switch import BaseSwitchEntity
from . import BaseDevice


class SmartPlug(BaseDevice):
    """Smart Plug."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "Smart Plug"

    def sensors(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SensorEntity]:
        """Available sensors for Smart Plug."""

        device_info_keys = self.remove_unnecessary_keys(set(self._device_info.keys()))

        count_keys = [
            "iot.resetCount",
        ]

        count_sensors = [
            CountSensorEntity(api, self, key)
            for key in count_keys
            if key in device_info_keys
        ]

        current_keys = [
            "iot.current",
            "iot.maxCur",
        ]

        current_sensors = [
            CurrentSensorEntity(api, self, key)
            for key in current_keys
            if key in device_info_keys
        ]

        duration_keys = [
            "iot.mqttErrTime",
            "iot.runTime",
            "iot.wifiErrTime",
        ]

        duration_sensors = [
            DurationSensorEntity(api, self, key, UnitOfTime.SECONDS)
            for key in duration_keys
            if key in device_info_keys
        ]

        frequency_keys = [
            "iot.freq",
        ]

        frequency_sensors = [
            FrequencySensorEntity(api, self, key)
            for key in frequency_keys
            if key in device_info_keys
        ]

        power_keys = [
            "iot.consWatt",
            "iot.geneWatt",
            "iot.maxWatts",
            "iot.watts",
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

        temperature_keys = [
            "iot.temp",
        ]

        temperature_sensors = [
            TemperateSensorEntity(api, self, key)
            for key in temperature_keys
            if key in device_info_keys
        ]

        voltage_keys = [
            "iot.volt",
        ]

        voltage_sensors = [
            VoltageSensorEntity(api, self, key)
            for key in voltage_keys
            if key in device_info_keys
        ]

        ignored_keys = [
            "iot.20_1",
            "iot.20_134",
            "iot.brightness",
            "iot.switchSta",
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

        found_keys = set(
            count_keys
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
            *count_sensors,
            *current_sensors,
            *diagnostic_sensors,
            *duration_sensors,
            *frequency_sensors,
            *power_sensors,
            *temperature_sensors,
            *voltage_sensors,
        ]

    def switches(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SwitchEntity]:
        """Available switches for Smart Plug."""

        return [
            BaseSwitchEntity(
                api,
                self,
                "iot.switchSta",
                command=lambda value: {
                    "cmdCode": "WN511_SOCKET_SET_PLUG_SWITCH_MESSAGE",
                    "params": {"plugSwitch": value},
                },
            )
        ]

    def numbers(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[NumberEntity]:
        """Available numbers for Smart Plug."""

        return [
            BrightnessEntity(
                api,
                self,
                "iot.brightness",
                min_value=0,
                max_value=100,
                command=lambda value: {
                    "cmdCode": "WN511_SOCKET_SET_BRIGHTNESS_PACK",
                    "params": {"brightness": round((value * 1023) / 100)},
                },
            )
        ]
