"""EcoFlow Smart Plug."""

from collections.abc import Sequence

from homeassistant.components.sensor import SensorEntity

from ..api import EcoFlowIoTOpenDataHolder
from ..sensor import (
    BinaryStateSensorEntity,
    CountSensorEntity,
    CurrentSensorEntity,
    DiagnosticSensorEntity,
    FrequencySensorEntity,
    PowerSensorEntity,
    TemperateSensorEntity,
    VoltageSensorEntity,
)
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

        binary_state_keys = [
            "iot.switchSta",
        ]

        binary_state_ensors = [
            BinaryStateSensorEntity(dataHolder, self, key)
            for key in binary_state_keys
            if key in device_info_keys
        ]

        count_keys = [
            "iot.resetCount",
        ]

        count_sensors = [
            CountSensorEntity(dataHolder, self, key)
            for key in count_keys
            if key in device_info_keys
        ]

        current_keys = [
            "iot.current",
            "iot.maxCur",
        ]

        current_sensors = [
            CurrentSensorEntity(dataHolder, self, key)
            for key in current_keys
            if key in device_info_keys
        ]

        current_keys = [
            "iot.current",
            "iot.maxCur",
        ]

        current_sensors = [
            CurrentSensorEntity(dataHolder, self, key)
            for key in current_keys
            if key in device_info_keys
        ]

        frequency_keys = [
            "iot.freq",
        ]

        frequency_sensors = [
            FrequencySensorEntity(dataHolder, self, key)
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
                dataHolder,
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
            TemperateSensorEntity(dataHolder, self, key)
            for key in temperature_keys
            if key in device_info_keys
        ]

        voltage_keys = [
            "iot.volt",
        ]

        voltage_sensors = [
            VoltageSensorEntity(dataHolder, self, key)
            for key in voltage_keys
            if key in device_info_keys
        ]

        ignored_keys = [
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
            binary_state_keys
            + count_keys
            + current_keys
            + frequency_keys
            + ignored_keys
            + power_keys
            + temperature_keys
            + voltage_keys
        )

        diagnostic_keys = device_info_keys - found_keys

        diagnostic_sensors = [
            DiagnosticSensorEntity(dataHolder, self, key, enabled=False)
            for key in diagnostic_keys
        ]
        return [
            *binary_state_ensors,
            *count_sensors,
            *current_sensors,
            *diagnostic_sensors,
            *frequency_sensors,
            *power_sensors,
            *temperature_sensors,
            *voltage_sensors,
        ]
