"""EcoFlow DELTA Max."""

from collections.abc import Sequence

from homeassistant.components.sensor import SensorEntity

from ..api import EcoFlowIoTOpenDataHolder
from ..sensor import (
    CapacitySensorEntity,
    CyclesSensorEntity,
    InMilliVoltSensorEntity,
    InWattsSensorEntity,
    InWattsSolarSensorEntity,
    LevelSensorEntity,
    MilliAmpSensorEntity,
    MilliVoltSensorEntity,
    MiscSensorEntity,
    OutMilliVoltSensorEntity,
    OutWattsDcSensorEntity,
    OutWattsSensorEntity,
    ProductInfoDetailsSensorEntity,
    RemainingTimeSensorEntity,
    StatusSensorEntity,
    TempSensorEntity,
    UsedTimeSensorEntity,
    VoltSensorEntity,
    WattsSensorEntity,
)
from . import BaseDevice


class DELTAMax(BaseDevice):
    """DELTA Max."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "DELTA Max"
        # self._client: EcoFlowIoTOpenAPIInterface

    def sensors(self, dataHolder: EcoFlowIoTOpenDataHolder) -> Sequence[SensorEntity]:
        """Available sensors for DELTA Max."""
        return [
            # bmsMaster
            MilliAmpSensorEntity(dataHolder, self, "bmsMaster.amp"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.balanceState"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.bmsFault"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.bqSysStatReg"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.cellId"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.cellNtcNum"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.cellSeriesNum"),
            # cellTemp needs to be processed as list
            MiscSensorEntity(dataHolder, self, "bmsMaster.cellTemp"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.cellVol"),
            CyclesSensorEntity(dataHolder, self, "bmsMaster.cycles"),
            CapacitySensorEntity(dataHolder, self, "bmsMaster.designCap"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.errCode"),
            LevelSensorEntity(dataHolder, self, "bmsMaster.f32ShowSoc"),
            CapacitySensorEntity(dataHolder, self, "bmsMaster.fullCap"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.hwEdition"),
            WattsSensorEntity(dataHolder, self, "bmsMaster.inputWatts"),
            TempSensorEntity(dataHolder, self, "bmsMaster.maxMosTemp"),
            MilliVoltSensorEntity(dataHolder, self, "bmsMaster.maxVolDiff"),
            TempSensorEntity(dataHolder, self, "bmsMaster.maxCellTemp"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.maxCellVol"),
            TempSensorEntity(dataHolder, self, "bmsMaster.minCellTemp"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.minCellVol"),
            TempSensorEntity(dataHolder, self, "bmsMaster.minMosTemp"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.mosState"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.num"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.openBmsIdx"),
            WattsSensorEntity(dataHolder, self, "bmsMaster.outputWatts"),
            CapacitySensorEntity(dataHolder, self, "bmsMaster.remainCap"),
            RemainingTimeSensorEntity(dataHolder, self, "bmsMaster.remainTime"),
            LevelSensorEntity(dataHolder, self, "bmsMaster.soc")
            .attr("bmsMaster.designCap", default=0)
            .attr("bmsMaster.fullCap", default=0)
            .attr("bmsMaster.remainCap", default=0),
            MiscSensorEntity(dataHolder, self, "bmsMaster.soh"),
            MiscSensorEntity(dataHolder, self, "bmsMaster.sysVer"),
            MilliAmpSensorEntity(dataHolder, self, "bmsMaster.tagChgAmp"),
            TempSensorEntity(dataHolder, self, "bmsMaster.temp")
            .attr("bmsMaster.minCellTemp", default=0)
            .attr("bmsMaster.maxCellTemp", default=0),
            MiscSensorEntity(dataHolder, self, "bmsMaster.type"),
            MilliVoltSensorEntity(dataHolder, self, "bmsMaster.vol")
            .attr("bmsMaster.minCellVol", default=0)
            .attr("bmsMaster.maxCellVol", default=0),
            # bmsSlave1, in this case DELTA Max Smart Battery
            MilliAmpSensorEntity(dataHolder, self, "bmsSlave1.amp"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.balanceState"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.bmsFault"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.bqSysStatReg"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.cellId"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.cellNtcNum"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.cellSeriesNum"),
            # cellTemp needs to be processed as list
            MiscSensorEntity(dataHolder, self, "bmsSlave1.cellTemp"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.cellVol"),
            CyclesSensorEntity(dataHolder, self, "bmsSlave1.cycles"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.errCode"),
            LevelSensorEntity(
                dataHolder, self, "bmsSlave1.f32ShowSoc", auto_enable=True
            )
            .attr("bmsSlave1.designCap", default=0)
            .attr("bmsSlave1.fullCap", default=0)
            .attr("bmsSlave1.remainCap", default=0)
            .attr("bmsSlave1.cycles", default=0),
            CapacitySensorEntity(dataHolder, self, "bmsSlave1.fullCap"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.hwEdition"),
            InWattsSensorEntity(dataHolder, self, "bmsSlave1.inputWatts"),
            TempSensorEntity(dataHolder, self, "bmsSlave1.maxCellTemp"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.maxCellVol"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.maxMosTemp"),
            MilliVoltSensorEntity(dataHolder, self, "bmsSlave1.maxVolDiff"),
            TempSensorEntity(dataHolder, self, "bmsSlave1.minCellTemp"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.minCellVol"),
            TempSensorEntity(dataHolder, self, "bmsSlave1.minMosTemp"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.mosState"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.num"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.openBmsIdx"),
            OutWattsSensorEntity(dataHolder, self, "bmsSlave1.outputWatts"),
            CapacitySensorEntity(dataHolder, self, "bmsSlave1.remainCap"),
            RemainingTimeSensorEntity(dataHolder, self, "bmsSlave1.remainTime"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.soc"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.soh"),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.sysVer"),
            MilliAmpSensorEntity(dataHolder, self, "bmsSlave1.tagChgAmp"),
            TempSensorEntity(dataHolder, self, "bmsSlave1.temp", auto_enable=True),
            MiscSensorEntity(dataHolder, self, "bmsSlave1.type"),
            VoltSensorEntity(dataHolder, self, "bmsSlave1.vol"),
            # ems
            MiscSensorEntity(dataHolder, self, "ems.bms0Online"),
            MiscSensorEntity(dataHolder, self, "ems.bms1Online"),
            MiscSensorEntity(dataHolder, self, "ems.bms2Online"),
            MiscSensorEntity(dataHolder, self, "ems.bmsModel"),
            MiscSensorEntity(dataHolder, self, "ems.bmsWarningState"),
            MilliAmpSensorEntity(dataHolder, self, "ems.chgAmp"),
            RemainingTimeSensorEntity(dataHolder, self, "ems.chgRemainTime"),
            MiscSensorEntity(dataHolder, self, "ems.chgCmd"),
            MiscSensorEntity(dataHolder, self, "ems.chgState"),
            MilliVoltSensorEntity(dataHolder, self, "ems.chgVol"),
            MiscSensorEntity(dataHolder, self, "ems.dsgCmd"),
            RemainingTimeSensorEntity(dataHolder, self, "ems.dsgRemainTime"),
            MiscSensorEntity(dataHolder, self, "ems.emsIsNormalFlag"),
            LevelSensorEntity(dataHolder, self, "ems.f32LcdShowSoc"),
            MiscSensorEntity(dataHolder, self, "ems.fanLevel"),
            LevelSensorEntity(dataHolder, self, "ems.lcdShowSoc"),
            MiscSensorEntity(dataHolder, self, "ems.maxAvailableNum"),
            MiscSensorEntity(dataHolder, self, "ems.maxChargeSoc"),
            MiscSensorEntity(dataHolder, self, "ems.maxCloseOilEbSoc"),
            MiscSensorEntity(dataHolder, self, "ems.minDsgSoc"),
            MiscSensorEntity(dataHolder, self, "ems.minOpenOilEbSoc"),
            MiscSensorEntity(dataHolder, self, "ems.openBmsIdx"),
            MiscSensorEntity(dataHolder, self, "ems.openUpsFlag"),
            MilliVoltSensorEntity(dataHolder, self, "ems.paraVolMax"),
            MilliVoltSensorEntity(dataHolder, self, "ems.paraVolMin"),
            # inv
            MiscSensorEntity(dataHolder, self, "inv.acDipSwitch"),
            MilliAmpSensorEntity(dataHolder, self, "inv.acInAmp"),
            MiscSensorEntity(dataHolder, self, "inv.acInFreq"),
            InMilliVoltSensorEntity(dataHolder, self, "inv.acInVol"),
            MiscSensorEntity(dataHolder, self, "inv.acPassByAutoEn"),
            MiscSensorEntity(dataHolder, self, "inv.cfgAcEnabled"),
            MiscSensorEntity(dataHolder, self, "inv.cfgAcOutFreq"),
            MilliVoltSensorEntity(dataHolder, self, "inv.cfgAcOutVoltage"),
            MiscSensorEntity(dataHolder, self, "inv.cfgAcWorkMode"),
            MiscSensorEntity(dataHolder, self, "inv.cfgAcXboost"),
            MiscSensorEntity(dataHolder, self, "inv.cfgFastChgWatts"),
            MiscSensorEntity(dataHolder, self, "inv.cfgSlowChgWatts"),
            MiscSensorEntity(dataHolder, self, "inv.cfgStandbyMin"),
            MiscSensorEntity(dataHolder, self, "inv.chargerType"),
            MiscSensorEntity(dataHolder, self, "inv.chgPauseFlag"),
            MilliAmpSensorEntity(dataHolder, self, "inv.dcInAmp"),
            TempSensorEntity(dataHolder, self, "inv.dcInTemp"),
            MilliVoltSensorEntity(dataHolder, self, "inv.dcInVol"),
            MiscSensorEntity(dataHolder, self, "inv.dischargeType"),
            MiscSensorEntity(dataHolder, self, "inv.errCode"),
            MiscSensorEntity(dataHolder, self, "inv.fanState"),
            InWattsSensorEntity(dataHolder, self, "inv.inputWatts"),
            MilliAmpSensorEntity(dataHolder, self, "inv.invOutAmp"),
            MiscSensorEntity(dataHolder, self, "inv.invOutFreq"),
            MiscSensorEntity(dataHolder, self, "inv.invType"),
            OutMilliVoltSensorEntity(dataHolder, self, "inv.invOutVol"),
            OutWattsSensorEntity(dataHolder, self, "inv.outputWatts"),
            TempSensorEntity(dataHolder, self, "inv.outTemp"),
            MiscSensorEntity(dataHolder, self, "inv.sysVer"),
            # kit
            MiscSensorEntity(dataHolder, self, "kit.availableDataLen"),
            MiscSensorEntity(dataHolder, self, "kit.maxKitNum"),
            # DELTA Max port 0, in this case DELTA Max Smart Battery
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 0, "appVersion"
            ),
            WattsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 0, "curPower"
            ),
            LevelSensorEntity(dataHolder, self, "kit.productInfoDetails", 0, "f32Soc"),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 0, "loaderVersion"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 0, "procedureState"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 0, "productDetail"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 0, "productType"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 0, "protocolAvaiFlag"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 0, "sn"
            ),
            LevelSensorEntity(dataHolder, self, "kit.productInfoDetails", 0, "soc"),
            # DELTA Max port 1, in this case PowerStream
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 1, "appVersion"
            ),
            WattsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 1, "curPower"
            ),
            LevelSensorEntity(dataHolder, self, "kit.productInfoDetails", 1, "f32Soc"),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 1, "loaderVersion"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 1, "procedureState"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 1, "productDetail"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 1, "productType"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 1, "protocolAvaiFlag"
            ),
            ProductInfoDetailsSensorEntity(
                dataHolder, self, "kit.productInfoDetails", 1, "sn"
            ),
            LevelSensorEntity(dataHolder, self, "kit.productInfoDetails", 1, "soc"),
            MiscSensorEntity(dataHolder, self, "kit.protocolVersion"),
            # mppt
            MilliAmpSensorEntity(dataHolder, self, "mppt.carOutAmp"),
            MilliVoltSensorEntity(dataHolder, self, "mppt.carOutVol"),
            WattsSensorEntity(dataHolder, self, "mppt.carOutWatts"),
            MiscSensorEntity(dataHolder, self, "mppt.carState"),
            TempSensorEntity(dataHolder, self, "mppt.carTemp"),
            MiscSensorEntity(dataHolder, self, "mppt.cfgChgType"),
            MiscSensorEntity(dataHolder, self, "mppt.cfgDcChgCurrent"),
            MiscSensorEntity(dataHolder, self, "mppt.chgPauseFlag"),
            MiscSensorEntity(dataHolder, self, "mppt.chgState"),
            MiscSensorEntity(dataHolder, self, "mppt.chgType"),
            MiscSensorEntity(dataHolder, self, "mppt.dc24vState"),
            TempSensorEntity(dataHolder, self, "mppt.dc24vTemp"),
            MilliAmpSensorEntity(dataHolder, self, "mppt.dcdc12vAmp"),
            MilliVoltSensorEntity(dataHolder, self, "mppt.dcdc12vVol"),
            WattsSensorEntity(dataHolder, self, "mppt.dcdc12vWatts"),
            MiscSensorEntity(dataHolder, self, "mppt.faultCode"),
            MilliAmpSensorEntity(dataHolder, self, "mppt.inAmp"),
            MilliVoltSensorEntity(dataHolder, self, "mppt.inVol"),
            InWattsSolarSensorEntity(dataHolder, self, "mppt.inWatts"),
            TempSensorEntity(dataHolder, self, "mppt.mpptTemp"),
            MilliAmpSensorEntity(dataHolder, self, "mppt.outAmp"),
            MilliVoltSensorEntity(dataHolder, self, "mppt.outVol"),
            OutWattsDcSensorEntity(dataHolder, self, "mppt.outWatts"),
            MiscSensorEntity(dataHolder, self, "mppt.swVer"),
            MiscSensorEntity(dataHolder, self, "mppt.xt60ChgType"),
            # pd
            MiscSensorEntity(dataHolder, self, "pd.beepState"),
            MiscSensorEntity(dataHolder, self, "pd.carState"),
            TempSensorEntity(dataHolder, self, "pd.carTemp"),
            UsedTimeSensorEntity(dataHolder, self, "pd.carUsedTime"),
            WattsSensorEntity(dataHolder, self, "pd.carWatts"),
            MiscSensorEntity(dataHolder, self, "pd.chgPowerAc"),
            MiscSensorEntity(dataHolder, self, "pd.chgPowerDc"),
            MiscSensorEntity(dataHolder, self, "pd.chgSunPower"),
            UsedTimeSensorEntity(dataHolder, self, "pd.dcInUsedTime"),
            MiscSensorEntity(dataHolder, self, "pd.dcOutState"),
            MiscSensorEntity(dataHolder, self, "pd.dsgPowerAc"),
            MiscSensorEntity(dataHolder, self, "pd.dsgPowerDc"),
            MiscSensorEntity(dataHolder, self, "pd.errCode"),
            # icons
            # MiscSensorEntity(dataHolder, self, "pd.iconAcFreqMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconAcFreqState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconBmsErrMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconBmsErrState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconBmsParallelMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconBmsParallelState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconBtMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconBtState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconCarMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconCarState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconChgStationMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconChgStationState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconCoGasMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconCoGasState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconEcoMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconEcoState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconFactoryMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconFactoryState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconFanMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconFanState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconGasGenMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconGasGenState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconHiTempMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconHiTempState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconInvParallelMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconInvParallelState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconLowTempMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconLowTempState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconOverloadMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconOverloadState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconPackHeaterMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconPackHeaterState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconRcMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconRcState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconRechgTimeMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconRechgTimeState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconSocUpsMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconSocUpsState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconSolarBracketMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconSolarBracketState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconSolarPanelMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconSolarPanelState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconTransSwMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconTransSwState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconTypecMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconTypecState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconUsbMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconUsbState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconWifiMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconWifiState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconWindGenMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconWindGenState"),
            # MiscSensorEntity(dataHolder, self, "pd.iconWirelessChgMode"),
            # MiscSensorEntity(dataHolder, self, "pd.iconWirelessChgState"),
            UsedTimeSensorEntity(dataHolder, self, "pd.invUsedTime"),
            MiscSensorEntity(dataHolder, self, "pd.kit0"),
            MiscSensorEntity(dataHolder, self, "pd.kit1"),
            MiscSensorEntity(dataHolder, self, "pd.kit2"),
            MiscSensorEntity(dataHolder, self, "pd.lcdBrightness"),
            MiscSensorEntity(dataHolder, self, "pd.lcdOffSec"),
            MiscSensorEntity(dataHolder, self, "pd.model"),
            UsedTimeSensorEntity(dataHolder, self, "pd.mpptUsedTime"),
            RemainingTimeSensorEntity(dataHolder, self, "pd.remainTime"),
            WattsSensorEntity(dataHolder, self, "pd.qcUsb1Watts"),
            WattsSensorEntity(dataHolder, self, "pd.qcUsb2Watts"),
            MiscSensorEntity(dataHolder, self, "pd.soc"),
            MiscSensorEntity(dataHolder, self, "pd.standByMode"),
            MiscSensorEntity(dataHolder, self, "pd.sysChgDsgState"),
            MiscSensorEntity(dataHolder, self, "pd.sysVer"),
            TempSensorEntity(dataHolder, self, "pd.typec1Temp"),
            WattsSensorEntity(dataHolder, self, "pd.typec1Watts"),
            TempSensorEntity(dataHolder, self, "pd.typec2Temp"),
            WattsSensorEntity(dataHolder, self, "pd.typec2Watts"),
            UsedTimeSensorEntity(dataHolder, self, "pd.typccUsedTime"),
            UsedTimeSensorEntity(dataHolder, self, "pd.usbqcUsedTime"),
            WattsSensorEntity(dataHolder, self, "pd.usb1Watts"),
            WattsSensorEntity(dataHolder, self, "pd.usb2Watts"),
            UsedTimeSensorEntity(dataHolder, self, "pd.usbUsedTime"),
            InWattsSensorEntity(dataHolder, self, "pd.wattsInSum"),
            OutWattsSensorEntity(dataHolder, self, "pd.wattsOutSum"),
            MiscSensorEntity(dataHolder, self, "pd.wifiAutoRcvy"),
            MiscSensorEntity(dataHolder, self, "pd.wifiRssi"),
            MiscSensorEntity(dataHolder, self, "pd.wifiVer"),
            WattsSensorEntity(dataHolder, self, "pd.wirelessWatts"),
            # Status
            StatusSensorEntity(dataHolder, self),
        ]
