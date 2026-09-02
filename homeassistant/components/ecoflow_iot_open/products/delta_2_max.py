"""EcoFlow DELTA 2 Max."""

from collections.abc import Sequence

from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity

from ..api import EcoFlowIoTOpenAPIInterface
from ..number import BatteryNumberEntity, ValueUpdateNumberEntity
from ..select import BaseSelectEntity, SelectEntity
from ..sensor import (
    BatterySensorEntity,
    BinaryStateSensorEntity,
    BrightnessSensorEntity,
    ChargingStateSensorEntity,
    CurrentSensorEntity,
    CyclesSensorEntity,
    DiagnosticSensorEntity,
    DurationSensorEntity,
    EnergySensorEntity,
    EnergyStorageSensorEntity,
    PowerSensorEntity,
    StatusSensorEntity,
    TemperateSensorEntity,
    VoltageSensorEntity,
)
from ..switch import BaseSwitchEntity
from . import BaseDevice


class DELTA2Max(BaseDevice):
    """EcoFlow DELTA 2 Max."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "DELTA 2 Max"

    def buttons(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[ButtonEntity]:
        """Available buttons for DELTA 2 Max."""
        return []

    def numbers(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[NumberEntity]:
        """Available numbers for DELTA 2 Max."""
        return [
            # BMS: SOC lower limit when discharging
            BatteryNumberEntity(
                api,
                self,
                "bms_emsStatus.minDsgSoc",
                command=lambda value: {
                    "moduleType": 2,
                    "operateType": "dsgCfg",
                    "params": {"minDsgSoc": value},
                },
                min_value=0,
                max_value=100,
            ),
            # BMS: UPS settings (max charging SOC)
            BatteryNumberEntity(
                api,
                self,
                "bms_emsStatus.maxChargeSoc",
                command=lambda value: {
                    "moduleType": 2,
                    "operateType": "upsConfig",
                    "params": {"maxChgSoc": value},
                },
                min_value=0,
                max_value=100,
            ),
            # BMS: SOC for turning on Smart Generator
            # BatteryNumberEntity(
            #     api,
            #     self,
            #     "bms_emsStatus.minOpenOilEb",
            #     command=lambda value: {
            #         "moduleType": 2,
            #         "operateType": "openOilSoc",
            #         "params": {"openOilSoc": value},
            #     },
            #     min_value=0,
            #     max_value=100,
            # ),
            # BMS: SOC for turning off Smart Generator
            # BatteryNumberEntity(
            #     api,
            #     self,
            #     "bms_emsStatus.maxCloseOilEb",
            #     command=lambda value: {
            #         "moduleType": 2,
            #         "operateType": "closeOilSoc",
            #         "params": {"closeOilSoc": value},
            #     },
            #     min_value=0,
            #     max_value=100,
            # ),
            # INV: AC fast charging power
            ValueUpdateNumberEntity(
                api,
                self,
                "inv.FastChgWatts",
                command=lambda value: {
                    "moduleType": 3,
                    "operateType": "acChgCfg",
                    "params": {"fastChgWatts": value},
                },
                min_value=100,
                max_value=2400,
            ),
            # INV: AC slow charging power
            ValueUpdateNumberEntity(
                api,
                self,
                "inv.SlowChgWatts",
                command=lambda value: {
                    "moduleType": 3,
                    "operateType": "acChgCfg",
                    "params": {"slowChgWatts": value},
                },
                min_value=100,
                max_value=700,
            ),
            # INV: AC standby duration
            ValueUpdateNumberEntity(
                api,
                self,
                "inv.standbyMin",
                command=lambda value: {
                    "moduleType": 3,
                    "operateType": "standbyTime",
                    "params": {"standbyMin": value},
                },
                min_value=0,
                max_value=1440,
            ),
            # MPPT: Car charging current (PV1)
            # TO_DO properly handle operate dcChgCfg with multiple params
            ValueUpdateNumberEntity(
                api,
                self,
                "mppt.dcChgCurrent",
                command=lambda value: {
                    "moduleType": 5,
                    "operateType": "dcChgCfg",
                    "params": {"dcChgCfg": value},
                },
                min_value=4000,
                max_value=8000,
                step=2000,
            ),
            # TO_DO properly handle operate dcChgCfg with multiple params
            ValueUpdateNumberEntity(
                api,
                self,
                "mppt.pv2DcChgCurrent",
                command=lambda value: {
                    "moduleType": 5,
                    "operateType": "dcChgCfg",
                    "params": {"dcChgCfg2": value},
                },
                min_value=4000,
                max_value=8000,
                step=2000,
            ),
            # MPPT: CAR standby duration
            ValueUpdateNumberEntity(
                api,
                self,
                "mppt.carStandbyMin",
                command=lambda value: {
                    "moduleType": 5,
                    "operateType": "standbyTime",
                    "params": {"standbyMin": value},
                },
                min_value=0,
                max_value=1440,
            ),
            # PD: Standby time
            ValueUpdateNumberEntity(
                api,
                self,
                "pd.standbyMin",
                command=lambda value: {
                    "moduleType": 1,
                    "operateType": "standbyTime",
                    "params": {"standbyMin": value},
                },
                min_value=0,
                max_value=1440,
            ),
            # PD: LCD screen timeout
            # TO_DO properly handle operateType lcdCfg with multiple params
            ValueUpdateNumberEntity(
                api,
                self,
                "pd.lcdOffSec",
                command=lambda value: {
                    "moduleType": 1,
                    "operateType": "lcdCfg",
                    "params": {"delayOff": value},
                },
                min_value=0,
                max_value=1800,
            ),
            # PD: Minimum SOC for AC Always On
            # TO_DO properly handly operateType newAcAutoOnCfg with multiple params
            BatteryNumberEntity(
                api,
                self,
                "pd.minAcSoc",
                command=lambda value: {
                    "moduleType": 1,
                    "operateType": "newAcAutoOnCfg",
                    "params": {"enabled": 1, "minAcSoc": value},
                },
                min_value=0,
                max_value=100,
            ),
            # PD: Backup reserve level
            # TO_DO properly handle operate watthConfig with multiple params
            BatteryNumberEntity(
                api,
                self,
                "pd.bpPowerSoc",
                command=lambda value: {
                    "moduleType": 1,
                    "operateType": "watthConfig",
                    "params": {"bpPowerSoc": value},
                },
                min_value=0,
                max_value=100,
            ),
        ]

    def selects(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SelectEntity]:
        """Available selects for DELTA 2 Max."""
        return [
            # MPPT: PV charging type (PV1)
            # BaseSelectEntity(
            #     api,
            #     self,
            #     "mppt.cfgChgType",
            #     command=lambda value: {
            #         "moduleType": 5,
            #         "operateType": "chaType",
            #         "params": {"chaType": value, "chaType2": value},
            #     },
            #     options={
            #         "Auto": 0,
            #         "MPPT": 1,
            #         "Adapter": 2,
            #     },
            # ),
            # INV: AC output frequency
            # BaseSelectEntity(
            #     api,
            #     self,
            #     "inv.cfgAcOutFreq",
            #     command=lambda value: {
            #         "moduleType": 3,
            #         "operateType": "acOutCfg",
            #         "params": {"out_freq": value},
            #     },
            #     options={
            #         "50 Hz": 1,
            #         "60 Hz": 2,
            #     },
            # ),
            # PD: LCD brightness level
            # TO_DO properly handle operateType lcdCfg with multiple params
            BaseSelectEntity(
                api,
                self,
                "pd.brightLevel",
                command=lambda value: {
                    "moduleType": 1,
                    "operateType": "lcdCfg",
                    "params": {"brighLevel": value},
                },
                options={
                    "Off": 0,
                    "Level 1": 1,
                    "Level 2": 2,
                    "Level 3": 3,
                },
            ),
        ]

    def switches(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SwitchEntity]:
        """Available switches for DELTA 2 Max."""
        return [
            # PD: Silent mode
            BaseSwitchEntity(
                api,
                self,
                "pd.beepMode",
                command=lambda value: {
                    "moduleType": 1,
                    "operateType": "quietCfg",
                    "params": {"enabled": int(not value)},
                },
            ),
            # PD: DC (USB) switch
            BaseSwitchEntity(
                api,
                self,
                "pd.dcOutState",
                command=lambda value: {
                    "moduleType": 1,
                    "operateType": "dcOutCfg",
                    "params": {"enabled": int(value)},
                },
            ),
            # PD: AC Always On
            # TO_DO properly handly operateType newAcAutoOnCfg with multiple params
            BaseSwitchEntity(
                api,
                self,
                "pd.newAcAutoOnCfg",
                command=lambda value: {
                    "moduleType": 1,
                    "operateType": "newAcAutoOnCfg",
                    "params": {"enabled": int(value)},
                },
            ),
            # PD: Energy management
            # TO_DO properly handle operate watthConfig with multiple params
            BaseSwitchEntity(
                api,
                self,
                "pd.watchIsConfig",
                command=lambda value: {
                    "moduleType": 1,
                    "operateType": "watthConfig",
                    "params": {"isConfig": int(not value)},
                },
            ),
            # MPPT: Car charging switch
            BaseSwitchEntity(
                api,
                self,
                "mppt.carState",
                command=lambda value: {
                    "moduleType": 5,
                    "operateType": "mpptCar",
                    "params": {"enabled": int(value)},
                },
            ),
            # INV: AC discharging switch
            BaseSwitchEntity(
                api,
                self,
                "inv.cfgAcEnabled",
                command=lambda value: {
                    "moduleType": 3,
                    "operateType": "acOutCfg",
                    "params": {"enabled": int(value)},
                },
            ),
            # INV: X-Boost switch
            BaseSwitchEntity(
                api,
                self,
                "inv.cfgAcXboost",
                command=lambda value: {
                    "moduleType": 3,
                    "operateType": "acOutCfg",
                    "params": {"xboost": int(value)},
                },
            ),
        ]

    def sensors(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SensorEntity]:
        """Available sensors for DELTA 2 Max."""

        device_info_keys = self.discard_unnecessary_keys(set(self._device_info.keys()))

        # Battery Sensors
        battery_keys = [
            "bms_bmsInfo.soh",
            "bms_bmsStatus.caleSoh",
            "bms_bmsStatus.cycSoh",
            "bms_bmsStatus.realSoh",
            "bms_bmsStatus.soh",
            "bms_slave_bmsSlaveInfo_1.soh",
            "bms_slave_bmsSlaveStatus_1.caleSoh",
            "bms_slave_bmsSlaveStatus_1.cycSoh",
            "bms_slave_bmsSlaveStatus_1.realSoh",
            "bms_slave_bmsSlaveStatus_1.soh",
            "bms_bmsStatus.actSoc",
            "bms_bmsStatus.diffSoc",
            "bms_bmsStatus.f32ShowSoc",
            "bms_bmsStatus.soc",
            "bms_bmsStatus.targetSoc",
            "bms_emsStatus.f32LcdShowSoc",
            "bms_emsStatus.lcdShowSoc",
            "bms_emsStatus.maxChargeSoc",
            "bms_emsStatus.minDsgSoc",
            "bms_slave_bmsSlaveStatus_1.actSoc",
            "bms_slave_bmsSlaveStatus_1.diffSoc",
            "bms_slave_bmsSlaveStatus_1.f32ShowSoc",
            "bms_slave_bmsSlaveStatus_1.soc",
            "bms_slave_bmsSlaveStatus_1.targetSoc",
            "pd.bpPowerSoc",
            "pd.minAcSoc",
            "pd.soc",
        ]

        battery_sensors = self.make_sensors(
            battery_keys, lambda key: BatterySensorEntity(api, self, key)
        )

        binary_state_keys = [
            "bms_bmsStatus.balanceState",
            "bms_bmsStatus.mosState",
            "bms_bmsStatus.sysState",
            "bms_emsStatus.bmsWarState",
            "bms_slave_bmsSlaveStatus_1.balanceState",
            "bms_slave_bmsSlaveStatus_1.mosState",
            "bms_slave_bmsSlaveStatus_1.sysState",
            "inv.fanState",
            "mppt.carState",
            "mppt.dc24vState",
            "pd.carState",
            "pd.dcOutState",
            "pd.otherKitState",
        ]

        binary_state_sensors = self.make_sensors(
            binary_state_keys, lambda key: BinaryStateSensorEntity(api, self, key)
        )

        charging_state_keys = [
            "bms_bmsStatus.chgState",
            "bms_emsStatus.chgState",
            "bms_emsStatus.sysChgDsgState",
            "bms_slave_bmsSlaveStatus_1.chgState",
            "mppt.chgState",
            "mppt.pv2ChgState",
            "pd.chgDsgState",
        ]

        charging_state_sensors = self.make_sensors(
            charging_state_keys,
            lambda key: ChargingStateSensorEntity(api, self, key),
        )

        # Current Sensors
        current_keys = [
            "bms_bmsStatus.amp",
            "bms_slave_bmsSlaveStatus_1.amp",
            "inv.acInAmp",
            "inv.dcInAmp",
            "inv.invOutAmp",
            "mppt.carOutAmp",
            "mppt.dcdc12vAmp",
            "mppt.inAmp",
            "mppt.outAmp",
            "mppt.pv2InAmp",
            "bms_emsStatus.chgAmp",
            "bms_bmsStatus.tagChgAmp",
            "bms_slave_bmsSlaveStatus_1.tagChgAmp",
            # "mppt.dcChgCurrent",
            # "mppt.pv2DcChgCurrent",
        ]
        current_sensors = self.make_sensors(
            current_keys, lambda key: CurrentSensorEntity(api, self, key)
        )

        cycles_keys = [
            "bms_bmsInfo.bsmCycles",
            "bms_bmsStatus.cycles",
            "bms_slave_bmsSlaveInfo_1.bsmCycles",
            "bms_slave_bmsSlaveStatus_1.cycles",
        ]

        cycles_sensors = self.make_sensors(
            cycles_keys, lambda key: CyclesSensorEntity(api, self, key)
        )

        # Duration Sensors
        duration_keys = [
            "bms_bmsStatus.remainTime",
            "bms_emsStatus.chgRemainTime",
            "bms_emsStatus.dsgRemainTime",
            "bms_slave_bmsSlaveStatus_1.remainTime",
            "pd.carUsedTime",
            "pd.dcInUsedTime",
            "pd.invUsedTime",
            "pd.remainTime",
            "pd.typecUsedTime",
            "pd.usbUsedTime",
            "pd.usbqcUsedTime",
            "bms_bmsInfo.highTempChgTime",
            "bms_bmsInfo.highTempTime",
            "bms_bmsInfo.lowTempChgTime",
            "bms_bmsInfo.lowTempTime",
            "bms_slave_bmsSlaveInfo_1.highTempChgTime",
            "bms_slave_bmsSlaveInfo_1.highTempTime",
            "bms_slave_bmsSlaveInfo_1.lowTempChgTime",
            "bms_slave_bmsSlaveInfo_1.lowTempTime",
            "pd.mpptUsedTime",
        ]
        duration_sensors = self.make_sensors(
            duration_keys, lambda key: DurationSensorEntity(api, self, key)
        )

        energy_keys = [
            "pd.chgPowerAC",
            "pd.chgPowerDC",
            "pd.chgSunPower",
            "pd.dsgPowerAC",
            "pd.dsgPowerDC",
            "bms_bmsInfo.accuChgEnergy",
            "bms_bmsInfo.accuDsgEnergy",
            "bms_slave_bmsSlaveInfo_1.accuChgEnergy",
            "bms_slave_bmsSlaveInfo_1.accuDsgEnergy",
        ]

        energy_sensors = self.make_sensors(
            energy_keys, lambda key: EnergySensorEntity(api, self, key)
        )

        energy_storage_keys = [
            "bms_bmsStatus.designCap",
            "bms_bmsStatus.fullCap",
            "bms_bmsStatus.remainCap",
            "bms_slave_bmsSlaveStatus_1.designCap",
            "bms_slave_bmsSlaveStatus_1.fullCap",
            "bms_slave_bmsSlaveStatus_1.remainCap",
        ]

        energy_storage_sensors = self.make_sensors(
            energy_storage_keys,
            lambda key: EnergyStorageSensorEntity(api, self, key),
        )

        # Power Sensors
        power_keys = [
            "bms_bmsStatus.inputWatts",
            "bms_bmsStatus.outputWatts",
            "bms_slave_bmsSlaveStatus_1.inputWatts",
            "bms_slave_bmsSlaveStatus_1.outputWatts",
            "inv.FastChgWatts",
            "inv.SlowChgWatts",
            "inv.acChgRatedPower",
            "inv.inputWatts",
            "inv.outputWatts",
            "mppt.carOutWatts",
            "mppt.dcdc12vWatts",
            "mppt.inWatts",
            "mppt.outWatts",
            "mppt.pv2InWatts",
            "pd.XT150Watts1",
            "pd.XT150Watts2",
            "pd.carWatts",
            "pd.invInWatts",
            "pd.invOutWatts",
            "pd.pv1ChargeWatts",
            "pd.pv2ChargeWatts",
            "pd.qcUsb1Watts",
            "pd.qcUsb2Watts",
            "pd.typec1Watts",
            "pd.typec2Watts",
            "pd.usb1Watts",
            "pd.usb2Watts",
            "pd.wattsInSum",
            "pd.wattsOutSum",
            "pd.wireWatts",
        ]
        power_sensors = self.make_sensors(
            power_keys, lambda key: PowerSensorEntity(api, self, key)
        )

        # Temperature Sensors
        temperature_keys = [
            "bms_bmsStatus.maxCellTemp",
            "bms_bmsStatus.maxMosTemp",
            "bms_bmsStatus.minCellTemp",
            "bms_bmsStatus.minMosTemp",
            "bms_bmsStatus.temp",
            "bms_slave_bmsSlaveStatus_1.maxCellTemp",
            "bms_slave_bmsSlaveStatus_1.maxMosTemp",
            "bms_slave_bmsSlaveStatus_1.minCellTemp",
            "bms_slave_bmsSlaveStatus_1.minMosTemp",
            "bms_slave_bmsSlaveStatus_1.temp",
            "inv.dcInTemp",
            "inv.outTemp",
            "mppt.carTemp",
            "mppt.dc24vTemp",
            "mppt.mpptTemp",
            "mppt.pv2MpptTemp",
            "pd.carTemp",
            "pd.typec1Temp",
            "pd.typec2Temp",
        ]
        temperature_sensors = self.make_sensors(
            temperature_keys, lambda key: TemperateSensorEntity(api, self, key)
        )

        # Voltage Sensors
        voltage_keys = [
            "bms_bmsStatus.maxCellVol",
            "bms_bmsStatus.maxVolDiff",
            "bms_bmsStatus.minCellVol",
            "bms_bmsStatus.vol",
            "bms_emsStatus.chgVol",
            "bms_slave_bmsSlaveStatus_1.maxCellVol",
            "bms_slave_bmsSlaveStatus_1.maxVolDiff",
            "bms_slave_bmsSlaveStatus_1.minCellVol",
            "bms_slave_bmsSlaveStatus_1.vol",
            "inv.acInVol",
            "inv.cfgAcOutVol",
            "inv.dcInVol",
            "inv.invOutVol",
            "mppt.carOutVol",
            "mppt.dcdc12vVol",
            "mppt.inVol",
            "mppt.outVol",
            "mppt.pv2InVol",
        ]
        voltage_sensors = self.make_sensors(
            voltage_keys, lambda key: VoltageSensorEntity(api, self, key)
        )

        found_keys = set(
            battery_keys
            + binary_state_keys
            + charging_state_keys
            + current_keys
            + cycles_keys
            + duration_keys
            + energy_keys
            + energy_storage_keys
            + power_keys
            + temperature_keys
            + voltage_keys
        )

        found_string_keys = set()

        # Extract string keys from found_keys
        for key in found_keys:
            if isinstance(key, str):
                found_string_keys.add(key)
            elif isinstance(key, tuple):
                found_string_keys.add(key[0])

        diagnostic_keys = device_info_keys - found_string_keys

        diagnostic_sensors = [
            DiagnosticSensorEntity(
                api,
                self,
                key,
                enabled=True,
            )
            for key in diagnostic_keys
        ]

        return (
            *battery_sensors,
            *binary_state_sensors,
            BrightnessSensorEntity(api, self, "pd.brightLevel"),
            *charging_state_sensors,
            *current_sensors,
            *cycles_sensors,
            *diagnostic_sensors,
            *duration_sensors,
            *energy_sensors,
            *energy_storage_sensors,
            *power_sensors,
            StatusSensorEntity(api, self, "status")
            .attr("last_updated")
            .attr("quota_allowed"),
            *temperature_sensors,
            *voltage_sensors,
        )
