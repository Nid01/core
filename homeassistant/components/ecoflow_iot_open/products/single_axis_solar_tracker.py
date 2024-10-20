"""EcoFlow Single Axis Solar Tracker."""

from collections.abc import Sequence

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfTime

from ..api import EcoFlowIoTOpenAPIInterface
from ..sensor import (
    BatterySensorEntity,
    BinaryStateSensorEntity,
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
    StatusSensorEntity,
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

    def sensors(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SensorEntity]:
        """Available sensors for Single Axis Solar Tracker."""

        device_info_keys = self.remove_unnecessary_keys(set(self._device_info.keys()))

        degree_keys = [
            "iot.angle",
            "iot.angleManual",
            "iot.angleTarget",
        ]

        degree_sensors = [
            DegreeSensorEntity(
                api,
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
            "status",
        ]

        found_keys = set(degree_keys + ignored_keys)

        diagnostic_keys = device_info_keys - found_keys

        diagnostic_sensors = [
            DiagnosticSensorEntity(api, self, key, enabled=False)
            for key in diagnostic_keys
        ]

        # DiagnosticSensorEntity(dataHolder, self, "iot.errCode"),
        # DiagnosticSensorEntity(dataHolder, self, "iot.shake"),
        # DiagnosticSensorEntity(dataHolder, self, "iot.switchState"),

        return [
            BatterySensorEntity(api, self, "iot.batteryPercent"),
            BinaryStateSensorEntity(api, self, "iot.switchState", "beeper"),
            ChargingStateSensorEntity(api, self, "iot.chargeState"),
            *degree_sensors,
            *diagnostic_sensors,
            DurationSensorEntity(api, self, "iot.chargeTimer", UnitOfTime.SECONDS),
            IlluminanceSensorEntity(api, self, "iot.lux"),
            IlluminanceGradeSensorEntity(api, self, "iot.luxGrade"),
            ModeSensorEntity(api, self, "iot.mode"),
            ScenesSensorEntity(api, self, "iot.scenes"),
            ModeAsWordSensorEntity(api, self, "iot.word"),
            ProtectionFromRainSensorEntity(
                api, self, "iot.switchState", "rain protection"
            ),
            ProtectionFromWindSensorEntity(
                api, self, "iot.switchState", "wind protection"
            ),
            StatusSensorEntity(api, self, "status").attr("last_updated"),
            TemperateSensorEntity(api, self, "iot.batteryTemperature"),
            WaterSensorEntity(api, self, "iot.water"),
            WindSensorEntity(api, self, "iot.wind"),
        ]

    def switches(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SwitchEntity]:
        """Available switches for Single Axis Solar Tracker."""

        return []

    def numbers(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[NumberEntity]:
        """Available numbers for Single Axis Solar Tracker."""

        return []
