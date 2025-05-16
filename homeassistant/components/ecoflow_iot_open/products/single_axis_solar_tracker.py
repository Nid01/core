"""EcoFlow Single Axis Solar Tracker."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfTime

from ..api import EcoFlowIoTOpenAPIInterface
from ..button import TrackAgainButton
from ..number import AngleNumberEntity, MinimumLightIntesityNumberEntity
from ..select import (
    LightTrackingSensitivitySelectEntity,
    ScenarioSelectEntity,
    WindSensitivitySelectEntity,
)
from ..sensor import (
    AngleSensorEntity,
    BatterySensorEntity,
    ChargingStateSensorEntity,
    DiagnosticSensorEntity,
    DurationSensorEntity,
    IlluminanceGradeSensorEntity,
    IlluminanceSensorEntity,
    ModeAsWordSensorEntity,
    ShakeSensorEntity,
    StatusSensorEntity,
    TemperateSensorEntity,
    WaterSensorEntity,
    WindSensorEntity,
)
from ..switch import (
    AlignmentModeSwitchEntity,
    BeeperSwitchEntity,
    DeviceSwitchEntity,
    RainProtectionSwitchEntity,
    WindProtectionSwitchEntity,
)
from . import (
    BaseDevice,
    single_axis_solar_tracker_pb2,  # https://developers.home-assistant.io/docs/asyncio_blocking_operations/#import_module
)


class SingleAxisSolarTracker(BaseDevice):
    """EcoFlow Single Axis Solar Tracker."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "Single Axis Solar Tracker"

    async def prepare_protobuf_message(self, command: dict[str, Any]) -> bytes | None:
        """Prepare the protobuf message for the single axis solar tracker."""
        sequence = int(datetime.now().timestamp())

        pdata = single_axis_solar_tracker_pb2.setValue(  # type: ignore[attr-defined]
            value=command.get("value"), value2=command.get("value2")
        )
        header = single_axis_solar_tracker_pb2.setHeader(  # type: ignore[attr-defined]
            pdata=pdata,
            src=32,
            dest=53,
            d_src=1,
            d_dest=1,
            check_type=3,
            cmd_func=2,
            cmd_id=command.get("cmdId"),
            data_len=command.get("dataLen", 2),
            need_ack=1,
            seq=sequence,
            product_id=1,
            version=19,
            payload_ver=1,
            **{"from": "HomeAssistant"},
            device_sn=self.serial_number,
        )
        message = single_axis_solar_tracker_pb2.setMessage(header=header)  # type: ignore[attr-defined]
        return message.SerializeToString()

    def buttons(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[ButtonEntity]:
        """Available buttons for Single Axis Solar Tracker."""

        return [
            TrackAgainButton(
                api,
                self,
                command=lambda: {
                    "cmdId": 19,
                    "value": 2,
                    "dataLen": 2,
                },
                title="track again",
            ),
        ]

    def numbers(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[NumberEntity]:
        """Available numbers for Single Axis Solar Tracker."""

        return [
            AngleNumberEntity(
                api,
                self,
                "iot.angleTarget",
                command=lambda value: {
                    "cmdId": 24,
                    "value": value - 10,
                    "dataLen": 2,
                },
                min_value=10,
                max_value=85,
            ),
            MinimumLightIntesityNumberEntity(
                api,
                self,
                "iot.strLux",
                command=lambda value, value2: {
                    "cmdId": 27,
                    "value": value,
                    "value2": value2,
                    "dataLen": 6,
                },
                min_value=10000,
                max_value=30000,
                step=5000,
                title="minimum light tracking sensitivity",
            ),
        ]

    def selects(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SelectEntity]:
        """Available selects for Single Axis Solar Tracker."""

        return [
            LightTrackingSensitivitySelectEntity(
                api,
                self,
                "iot.lightSen",
                command=lambda value, value2: {
                    "cmdId": 27,
                    "value": value,
                    "value2": value2,
                    "dataLen": 6,
                },
                options=["low", "medium", "high"],
                title="light tracking sensitivity",
            ),
            ScenarioSelectEntity(
                api,
                self,
                "iot.scenes",
                command=lambda value: {
                    "cmdId": 17,
                    "value": value,
                    "dataLen": 2,
                },
                options=["balcony", "courtyard"],
                title="scenario",
            ),
            WindSensitivitySelectEntity(
                api,
                self,
                "iot.sharkSen",
                command=lambda value: {
                    "cmdId": 22,
                    "value2": value,
                    "dataLen": 2,
                },
                options=["low", "medium", "high"],
                title="wind sensitivity",
            ),
        ]

    def sensors(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SensorEntity]:
        """Available sensors for Single Axis Solar Tracker."""

        device_info_keys = self.remove_unnecessary_keys(set(self._device_info.keys()))

        angle_keys = [
            "iot.angle",
            "iot.angleManual",
        ]

        angle_sensors = [
            AngleSensorEntity(
                api,
                self,
                key,
            )
            for key in angle_keys
            if key in device_info_keys
        ]

        ignored_keys = [
            "iot.angleTarget",
            "iot.batteryPercent",
            "iot.batteryTemperature",
            "iot.chargeState",
            "iot.chargeTimer",
            "iot.lightSen",
            "iot.lux",
            "iot.luxGrade",
            "iot.mode",
            "iot.scenes",
            "iot.sharkSen",
            "iot.strLux",
            "iot.water",
            "iot.wind",
            "iot.word",
            "iot.shake",
            "status",
        ]

        found_keys = set(angle_keys + ignored_keys)

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
            ChargingStateSensorEntity(api, self, "iot.chargeState"),
            *angle_sensors,
            *diagnostic_sensors,
            DurationSensorEntity(api, self, "iot.chargeTimer", UnitOfTime.SECONDS),
            IlluminanceSensorEntity(api, self, "iot.lux"),
            IlluminanceGradeSensorEntity(api, self, "iot.luxGrade"),
            ModeAsWordSensorEntity(api, self, "iot.word"),
            StatusSensorEntity(api, self, "status").attr("last_updated"),
            TemperateSensorEntity(api, self, "iot.batteryTemperature"),
            WaterSensorEntity(api, self, "iot.water", title="water detection"),
            WindSensorEntity(api, self, "iot.wind", title="wind detection"),
            ShakeSensorEntity(api, self, "iot.shake", title="shake detection"),
        ]

    def switches(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SwitchEntity]:
        """Available switches for Single Axis Solar Tracker."""

        return [
            AlignmentModeSwitchEntity(
                api,
                self,
                "iot.mode",
                command=lambda value: {
                    "cmdId": 19,
                    "value": value,
                    "dataLen": 2,
                },
                title="auto alignment mode",
            ),
            BeeperSwitchEntity(
                api,
                self,
                "iot.switchState",
                command=lambda value: {
                    "cmdId": 20,
                    "value": value,
                    "dataLen": 2,
                },
                title="beeper",
            ),
            DeviceSwitchEntity(
                api,
                self,
                "iot.word",
                command=lambda value: {
                    "cmdId": 18,
                    "value": 1 if value else 2,
                    "dataLen": 2,
                },
                title="device",
            ),
            RainProtectionSwitchEntity(
                api,
                self,
                "iot.switchState",
                command=lambda value: {
                    "cmdId": 21,
                    "value": value,
                    "dataLen": 2,
                },
                title="rain protection",
            ),
            WindProtectionSwitchEntity(
                api,
                self,
                "iot.switchState",
                command=lambda value: {
                    "cmdId": 22,
                    "value": value,
                    "dataLen": 2,
                },
                title="wind protection",
            ),
        ]
