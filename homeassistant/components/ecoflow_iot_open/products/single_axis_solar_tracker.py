"""EcoFlow Single Axis Solar Tracker."""

from collections.abc import Sequence

from homeassistant.components.sensor import SensorEntity

from ..api import EcoFlowIoTOpenDataHolder
from ..sensor import (
    AngleSensorEntity,
    BeeperSensorEntity,
    ChargingStateSensorEntity,
    LevelSensorEntity,
    LuxGradeSensorEntity,
    LuxSensorEntity,
    MiscSensorEntity,
    ModeSensorEntity,
    ModeWordSensorEntity,
    RainProtectionSensorEntity,
    ScenesSensorEntity,
    SecondsRemainSensorEntity,
    TempSensorEntity,
    WaterSensorEntity,
    WindProtectionSensorEntity,
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
        return [
            LevelSensorEntity(dataHolder, self, "iot.batteryPercent"),
            LuxSensorEntity(dataHolder, self, "iot.lux"),
            AngleSensorEntity(dataHolder, self, "iot.angle"),
            AngleSensorEntity(dataHolder, self, "iot.angleManual"),
            AngleSensorEntity(dataHolder, self, "iot.angleTarget"),
            TempSensorEntity(dataHolder, self, "iot.batteryTemperature"),
            ChargingStateSensorEntity(dataHolder, self, "iot.chargeState"),
            SecondsRemainSensorEntity(dataHolder, self, "iot.chargeTimer"),
            MiscSensorEntity(dataHolder, self, "iot.errCode"),
            LuxGradeSensorEntity(dataHolder, self, "iot.luxGrade"),
            ModeSensorEntity(dataHolder, self, "iot.mode"),
            ScenesSensorEntity(dataHolder, self, "iot.scenes"),
            MiscSensorEntity(dataHolder, self, "iot.shake"),
            MiscSensorEntity(dataHolder, self, "iot.switchState"),
            BeeperSensorEntity(dataHolder, self, "iot.switchState", "beeper"),
            RainProtectionSensorEntity(
                dataHolder, self, "iot.switchState", "rain protection"
            ),
            WindProtectionSensorEntity(
                dataHolder, self, "iot.switchState", "wind protection"
            ),
            WaterSensorEntity(dataHolder, self, "iot.water"),
            WindSensorEntity(dataHolder, self, "iot.wind"),
            ModeWordSensorEntity(dataHolder, self, "iot.word"),
        ]
