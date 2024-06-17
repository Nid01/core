"""EcoFlow Single Axis Solar Tracker."""

from collections.abc import Sequence

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTime

from ..api import EcoFlowIoTOpenDataHolder
from ..sensor import (
    BatterySensorEntity,
    BeeperSensorEntity,
    ChargingStateSensorEntity,
    DegreeSensorEntity,
    DiagnosticSensorEntity,
    DurationSensorEntity,
    IlluminanceGradeSensorEntity,
    IlluminanceSensorEntity,
    ModeAsWordSensorEntity,
    ModeSensorEntity,
    ProtectionFromRainSensorEntity,
    ProtectionFromWindSensorEntity,
    ScenesSensorEntity,
    TemperateSensorEntity,
    WaterSensorEntity,
    WindSensorEntity,
)
from . import BaseDevice


class SingleAxisSolarTracker(BaseDevice):
    """Single Axis Solar Tracker."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "Single Axis Solar Tracker"

    def sensors(self, dataHolder: EcoFlowIoTOpenDataHolder) -> Sequence[SensorEntity]:
        """Available sensors for Single Axis Solar Tracker."""

        device_info_keys = set(self._device_info.keys())
        device_info_keys.remove("deviceName")
        device_info_keys.remove("online")
        device_info_keys.remove("sn")

        degree_keys = [
            "iot.angle",
            "iot.angleManual",
            "iot.angleTarget",
        ]

        degree_sensors = [
            DegreeSensorEntity(
                dataHolder,
                self,
                key,
            )
            for key in degree_keys
            if key in device_info_keys
        ]

        ignored_keys = [
            "iot.batteryPercent",
            "iot.chargeState",
            "iot.chargeTimer",
            "iot.lux",
            "iot.luxGrade",
            "iot.mode",
            "iot.scenes",
            "iot.word",
            "iot.batteryTemperature",
            "iot.water",
            "iot.wind",
        ]

        found_keys = set(degree_keys + ignored_keys)

        diagnostic_keys = device_info_keys - found_keys

        diagnostic_sensors = [
            DiagnosticSensorEntity(dataHolder, self, key) for key in diagnostic_keys
        ]

        # DiagnosticSensorEntity(dataHolder, self, "iot.errCode"),
        # DiagnosticSensorEntity(dataHolder, self, "iot.shake"),
        # DiagnosticSensorEntity(dataHolder, self, "iot.switchState"),

        return [
            BatterySensorEntity(dataHolder, self, "iot.batteryPercent"),
            BeeperSensorEntity(dataHolder, self, "iot.switchState", "beeper"),
            ChargingStateSensorEntity(dataHolder, self, "iot.chargeState"),
            *degree_sensors,
            *diagnostic_sensors,
            DurationSensorEntity(
                dataHolder, self, "iot.chargeTimer", UnitOfTime.SECONDS
            ),
            IlluminanceSensorEntity(dataHolder, self, "iot.lux"),
            IlluminanceGradeSensorEntity(dataHolder, self, "iot.luxGrade"),
            ModeSensorEntity(dataHolder, self, "iot.mode"),
            ScenesSensorEntity(dataHolder, self, "iot.scenes"),
            ModeAsWordSensorEntity(dataHolder, self, "iot.word"),
            ProtectionFromRainSensorEntity(
                dataHolder, self, "iot.switchState", "rain protection"
            ),
            ProtectionFromWindSensorEntity(
                dataHolder, self, "iot.switchState", "wind protection"
            ),
            TemperateSensorEntity(dataHolder, self, "iot.batteryTemperature"),
            WaterSensorEntity(dataHolder, self, "iot.water"),
            WindSensorEntity(dataHolder, self, "iot.wind"),
        ]
