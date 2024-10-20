"""EcoFlow DELTA Max."""

from collections.abc import Sequence

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfElectricCurrent, UnitOfTime

from ..api import EcoFlowIoTOpenAPIInterface
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
    ProductInfoDetailSensorEntity,
    # StatusSensorEntity,
    TemperateSensorEntity,
    VoltageSensorEntity,
)
from . import BaseDevice


class DELTAMax(BaseDevice):
    """DELTA Max."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "DELTA Max"
        # self._client: EcoFlowIoTOpenAPIInterface

    def sensors(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SensorEntity]:
        """Available sensors for DELTA Max."""

        device_info_keys = self.remove_unnecessary_keys(set(self._device_info.keys()))

        def add_cell_sensors(cell_key, sensors: list, SensorEntityClass):
            if cell_key in device_info_keys:
                cell_keys = [
                    (cell_key, index)
                    for index in range(len(self._device_info[cell_key]))
                ]
                cell_sensors = [
                    SensorEntityClass(api, self, key[0], list_position=key[1])
                    for key in cell_keys
                ]
                sensors.extend(cell_sensors)

        battery_keys = [
            "bmsMaster.f32ShowSoc",
            # .attr("bmsMaster.designCap", default=0)
            # .attr("bmsMaster.fullCap", default=0)
            # .attr("bmsMaster.remainCap", default=0),
            # .attr("bmsMaster.cycles", default=0),
            "bmsMaster.soc",
            "bmsSlave1.f32ShowSoc",
            # .attr("bmsSlave1.designCap", default=0)
            # .attr("bmsSlave1.fullCap", default=0)
            # .attr("bmsSlave1.remainCap", default=0)
            # .attr("bmsSlave1.cycles", default=0),
            "bmsSlave1.soc",
            "ems.f32LcdShowSoc",
            "ems.lcdShowSoc",
            "pd.soc",
            # ("kit.productInfoDetails", 0, "f32Soc"),
            # ("kit.productInfoDetails", 0, "soc"),
            # ("kit.productInfoDetails", 1, "f32Soc"),
            # ("kit.productInfoDetails", 1, "soc"),
        ]

        battery_sensors = [
            BatterySensorEntity(api, self, key)
            for key in battery_keys
            if key in device_info_keys
        ]

        binary_state_keys = [
            "inv.fanState",
        ]

        binary_state_sensors = [
            BinaryStateSensorEntity(api, self, key)
            for key in binary_state_keys
            if key in device_info_keys
        ]

        charging_state_keys = [
            "pd.sysChgDsgState",
            "ems.chgState",
        ]

        charging_state_sensors = [
            ChargingStateSensorEntity(api, self, key)
            for key in charging_state_keys
            if key in device_info_keys
        ]

        current_keys = [
            "bmsMaster.amp",
            "bmsMaster.tagChgAmp",
            "bmsSlave1.amp",
            "bmsSlave1.tagChgAmp",
            "ems.chgAmp",
            "inv.acInAmp",
            "inv.dcInAmp",
            "inv.invOutAmp",
            "mppt.carOutAmp",
            "mppt.cfgDcChgCurrent",
            "mppt.dcdc12vAmp",
            "mppt.inAmp",
            "mppt.outAmp",
        ]

        current_units = {
            "mppt.carOutAmp": UnitOfElectricCurrent.MILLIAMPERE,
        }

        current_sensors = [
            CurrentSensorEntity(
                api,
                self,
                key,
                current_units.get(key, UnitOfElectricCurrent.AMPERE),
            )
            for key in current_keys
            if key in device_info_keys
        ]

        cycles_keys = [
            "bmsMaster.cycles",
            "bmsSlave1.cycles",
        ]

        cycles_sensors = [
            CyclesSensorEntity(api, self, key)
            for key in cycles_keys
            if key in device_info_keys
        ]

        energy_keys = [
            "pd.chgPowerAc",
            "pd.chgPowerDc",
            "pd.chgSunPower",
            "pd.dsgPowerAc",
            "pd.dsgPowerDc",
        ]

        energy_sensors = [
            EnergySensorEntity(api, self, key)
            for key in energy_keys
            if key in device_info_keys
        ]

        energy_storage_keys = [
            "bmsMaster.designCap",
            "bmsMaster.fullCap",
            "bmsMaster.remainCap",
            "bmsSlave1.designCap",
            "bmsSlave1.fullCap",
            "bmsSlave1.remainCap",
        ]

        energy_storage_sensors = [
            EnergyStorageSensorEntity(api, self, key)
            for key in energy_storage_keys
            if key in device_info_keys
        ]

        duration_keys = [
            "bmsMaster.remainTime",
            "bmsSlave1.remainTime",
            "ems.chgRemainTime",
            "ems.dsgRemainTime",
            "inv.cfgStandbyMin",
            "pd.carUsedTime",
            "pd.dcInUsedTime",
            "pd.invUsedTime",
            "pd.lcdOffSec",
            "pd.mpptUsedTime",
            "pd.remainTime",
            "pd.typccUsedTime",
            "pd.usbqcUsedTime",
            "pd.usbUsedTime",
            "pd.standByMode",
        ]

        duration_units = {
            "pd.lcdOffSec": UnitOfTime.SECONDS,
        }

        duration_sensors = [
            DurationSensorEntity(
                api,
                self,
                key,
                duration_units.get(key, UnitOfTime.MINUTES),
            )
            for key in duration_keys
            if key in device_info_keys
        ]

        power_keys = [
            "bmsMaster.inputWatts",
            "bmsMaster.outputWatts",
            "bmsSlave1.inputWatts",
            "bmsSlave1.outputWatts",
            "inv.cfgFastChgWatts",
            "inv.cfgSlowChgWatts",
            "inv.inputWatts",
            "inv.outputWatts",
            # ("kit.productInfoDetails", 0, "curPower"),
            # ("kit.productInfoDetails", 1, "curPower"),
            "mppt.carOutWatts",
            "mppt.dcdc12vWatts",
            "mppt.inWatts",
            "mppt.outWatts",
            "pd.carWatts",
            "pd.qcUsb1Watts",
            "pd.qcUsb2Watts",
            "pd.typec1Watts",
            "pd.typec2Watts",
            "pd.usb1Watts",
            "pd.usb2Watts",
            "pd.wirelessWatts",
            "pd.wattsInSum",
            "pd.wattsOutSum",
        ]

        power_factors = {
            "mppt.inWatts": 0.1,
            "mppt.outWatts": 0.1,
        }

        power_sensors = [
            PowerSensorEntity(
                api,
                self,
                key,
                power_factors.get(key, 1),
            )
            for key in power_keys
            if key in device_info_keys
        ]

        temperature_keys = [
            "bmsMaster.maxCellTemp",
            "bmsMaster.maxMosTemp",
            "bmsMaster.minCellTemp",
            "bmsMaster.minMosTemp",
            "bmsMaster.temp",
            # .attr("bmsMaster.minCellTemp", default=0)
            # .attr("bmsMaster.maxCellTemp", default=0),
            "bmsSlave1.maxCellTemp",
            "bmsSlave1.maxMosTemp",
            "bmsSlave1.minCellTemp",
            "bmsSlave1.minMosTemp",
            "bmsSlave1.temp",
            # .attr("bmsSlave1.minCellTemp", default=0)
            # .attr("bmsSlave1.maxCellTemp", default=0),
            "inv.dcInTemp",
            "inv.outTemp",
            "mppt.carTemp",
            "mppt.dc24vTemp",
            "mppt.mpptTemp",
            "pd.carTemp",
            "pd.typec1Temp",
            "pd.typec2Temp",
        ]

        temperature_sensors = [
            TemperateSensorEntity(api, self, key)
            for key in temperature_keys
            if key in device_info_keys
        ]

        add_cell_sensors(
            "bmsMaster.cellTemp", temperature_sensors, TemperateSensorEntity
        )
        add_cell_sensors(
            "bmsSlave1.cellTemp", temperature_sensors, TemperateSensorEntity
        )

        voltage_keys = [
            "bmsMaster.vol",
            # .attr("bmsMaster.minCellVol", default=0)
            # .attr("bmsMaster.maxCellVol", default=0),
            "bmsMaster.maxCellVol",
            "bmsMaster.minCellVol",
            "bmsMaster.maxVolDiff",
            "bmsSlave1.vol",
            # .attr("bmsSlave1.minCellVol", default=0)
            # .attr("bmsSlave1.maxCellVol", default=0),
            "bmsSlave1.maxCellVol",
            "bmsSlave1.minCellVol",
            "bmsSlave1.maxVolDiff",
            "ems.chgVol",
            "ems.paraVolMax",
            "ems.paraVolMin",
            "inv.acInVol",
            "inv.cfgAcOutVoltage",
            "inv.dcInVol",
            "inv.invOutVol",
            "mppt.carOutVol",
            "mppt.dcdc12vVol",
            "mppt.inVol",
            "mppt.outVol",
        ]

        voltage_sensors = [
            VoltageSensorEntity(api, self, key)
            for key in voltage_keys
            if key in device_info_keys
        ]

        add_cell_sensors("bmsMaster.cellVol", voltage_sensors, VoltageSensorEntity)
        add_cell_sensors("bmsSlave1.cellVol", voltage_sensors, VoltageSensorEntity)

        product_info_detail_keys = []
        product_info_detail_sensors = []

        product_info_details_key = "kit.productInfoDetails"
        if product_info_details_key in device_info_keys:
            # Define the detail keys
            detail_keys = [
                "appVersion",
                "loaderVersion",
                "procedureState",
                "productDetail",
                "productType",
                "protocolAvaiFlag",
                "sn",
            ]
            product_info_detail_keys = [
                (product_info_details_key, index, detail_key)
                for index in range(len(self._device_info[product_info_details_key]))
                for detail_key in detail_keys
            ]
            product_info_detail_sensors = [
                ProductInfoDetailSensorEntity(api, self, key[0], key[1], key[2])
                for key in product_info_detail_keys
            ]

        ignored_keys = [
            "bmsMaster.cellTemp",
            "bmsSlave1.cellTemp",
            "bmsMaster.cellVol",
            "bmsSlave1.cellVol",
            "pd.beepMode",
            "pd.lcdBrightness",
            # icons
            "pd.iconAcFreqMode",
            "pd.iconAcFreqState",
            "pd.iconBmsErrMode",
            "pd.iconBmsErrState",
            "pd.iconBmsParallelMode",
            "pd.iconBmsParallelState",
            "pd.iconBtMode",
            "pd.iconBtState",
            "pd.iconCarMode",
            "pd.iconCarState",
            "pd.iconChgStationMode",
            "pd.iconChgStationState",
            "pd.iconCoGasMode",
            "pd.iconCoGasState",
            "pd.iconEcoMode",
            "pd.iconEcoState",
            "pd.iconFactoryMode",
            "pd.iconFactoryState",
            "pd.iconFanMode",
            "pd.iconFanState",
            "pd.iconGasGenMode",
            "pd.iconGasGenState",
            "pd.iconHiTempMode",
            "pd.iconHiTempState",
            "pd.iconInvParallelMode",
            "pd.iconInvParallelState",
            "pd.iconLowTempMode",
            "pd.iconLowTempState",
            "pd.iconOverloadMode",
            "pd.iconOverloadState",
            "pd.iconPackHeaterMode",
            "pd.iconPackHeaterState",
            "pd.iconRcMode",
            "pd.iconRcState",
            "pd.iconRechgTimeMode",
            "pd.iconRechgTimeState",
            "pd.iconSocUpsMode",
            "pd.iconSocUpsState",
            "pd.iconSolarBracketMode",
            "pd.iconSolarBracketState",
            "pd.iconSolarPanelMode",
            "pd.iconSolarPanelState",
            "pd.iconTransSwMode",
            "pd.iconTransSwState",
            "pd.iconTypecMode",
            "pd.iconTypecState",
            "pd.iconUsbMode",
            "pd.iconUsbState",
            "pd.iconWifiMode",
            "pd.iconWifiState",
            "pd.iconWindGenMode",
            "pd.iconWindGenState",
            "pd.iconWirelessChgMode",
            "pd.iconWirelessChgState",
        ]

        found_keys = set(
            battery_keys
            + binary_state_keys
            + charging_state_keys
            + current_keys
            + cycles_keys
            + duration_keys
            + energy_keys
            + energy_storage_keys
            + ignored_keys
            + power_keys
            + [product_info_details_key]
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
            DiagnosticSensorEntity(api, self, key, enabled=False)
            for key in diagnostic_keys
        ]

        return [
            *binary_state_sensors,
            *battery_sensors,
            BrightnessSensorEntity(api, self, "pd.lcdBrightness"),
            *charging_state_sensors,
            *current_sensors,
            *cycles_sensors,
            *diagnostic_sensors,
            *duration_sensors,
            *energy_sensors,
            *energy_storage_sensors,
            *power_sensors,
            *product_info_detail_sensors,
            # StatusSensorEntity(api, self),
            *temperature_sensors,
            *voltage_sensors,
        ]

    def switches(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[SwitchEntity]:
        """Available switches for DELTA Max."""

        return [
            # parameters are not identical between Delta2Max and not documented DeltaMax
            # BaseSwitchEntity(
            #     api,
            #     self,
            #     "pd.beepMode",
            #     command=lambda value: {
            #         "moduleType": 1,
            #         "operateType": "quietCfg",
            #         "params": {"enabled": value},
            #     },  # type: ignore
            # )
        ]

    def numbers(self, api: EcoFlowIoTOpenAPIInterface) -> Sequence[NumberEntity]:
        """Available numbers for DELTA Max."""

        return []
