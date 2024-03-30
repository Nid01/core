"""EcoFlow DELTA Max."""

from typing import Union

from . import Device


class DELTAMax(Device):
    """DELTA Max."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "DELTA Max"

    @property
    def battery_level(self) -> Union[int, None]:
        """Return the value 0-100? of the battery level."""
        return self._device_info.get("bmsMaster.soc")


# quota all response
# {
#   "bmsMaster.amp": -3949,
#   "bmsMaster.balanceState": 0,
#   "bmsMaster.bmsFault": 0,
#   "bmsMaster.bqSysStatReg": 128,
#   "bmsMaster.cellId": 1,
#   "bmsMaster.cellNtcNum": 0,
#   "bmsMaster.cellSeriesNum": 14,
#   "bmsMaster.cellTemp": [
#     29,
#     12374,
#     12334,
#     12334
#   ],
#   "bmsMaster.cellVol": [
#     3794,
#     3797,
#     3794,
#     3797,
#     3797,
#     3796,
#     3799,
#     0,
#     0,
#     0,
#     0,
#     0,
#     0,
#     0,
#     7426
#   ],
#   "bmsMaster.cycles": 89,
#   "bmsMaster.designCap": 40000,
#   "bmsMaster.errCode": 0,
#   "bmsMaster.f32ShowSoc": 40.665787,
#   "bmsMaster.fullCap": 39200,
#   "bmsMaster.hwEdition": [
#     0,
#     0,
#     0,
#     0,
#     0,
#     0
#   ],
#   "bmsMaster.inputWatts": 0,
#   "bmsMaster.maxCellTemp": 29,
#   "bmsMaster.maxCellVol": 3803,
#   "bmsMaster.maxMosTemp": 31,
#   "bmsMaster.maxVolDiff": 9,
#   "bmsMaster.minCellTemp": 29,
#   "bmsMaster.minCellVol": 3794,
#   "bmsMaster.minMosTemp": 31,
#   "bmsMaster.mosState": 3,
#   "bmsMaster.num": 0,
#   "bmsMaster.openBmsIdx": 3,
#   "bmsMaster.outputWatts": 0,
#   "bmsMaster.remainCap": 15940,
#   "bmsMaster.remainTime": 0,
#   "bmsMaster.soc": 41,
#   "bmsMaster.soh": 100,
#   "bmsMaster.sysVer": 16843811,
#   "bmsMaster.tagChgAmp": 32000,
#   "bmsMaster.temp": 29,
#   "bmsMaster.type": 1,
#   "bmsMaster.vol": 53312,
#   "bmsSlave1.amp": -4051,
#   "bmsSlave1.balanceState": 0,
#   "bmsSlave1.bmsFault": 0,
#   "bmsSlave1.bqSysStatReg": 128,
#   "bmsSlave1.cellId": 1,
#   "bmsSlave1.cellNtcNum": 0,
#   "bmsSlave1.cellSeriesNum": 14,
#   "bmsSlave1.cellTemp": [
#     26,
#     12374,
#     12334,
#     12334
#   ],
#   "bmsSlave1.cellVol": [
#     3799,
#     3789,
#     3798,
#     3793,
#     3798,
#     3795,
#     3803,
#     0,
#     0,
#     0,
#     0,
#     0,
#     0,
#     0,
#     6658
#   ],
#   "bmsSlave1.cycles": 63,
#   "bmsSlave1.designCap": 40000,
#   "bmsSlave1.errCode": 0,
#   "bmsSlave1.f32ShowSoc": 38.358414,
#   "bmsSlave1.fullCap": 39200,
#   "bmsSlave1.hwEdition": [
#     0,
#     0,
#     0,
#     0,
#     0,
#     0
#   ],
#   "bmsSlave1.inputWatts": 0,
#   "bmsSlave1.maxCellTemp": 26,
#   "bmsSlave1.maxCellVol": 3803,
#   "bmsSlave1.maxMosTemp": 29,
#   "bmsSlave1.maxVolDiff": 22,
#   "bmsSlave1.minCellTemp": 26,
#   "bmsSlave1.minCellVol": 3781,
#   "bmsSlave1.minMosTemp": 29,
#   "bmsSlave1.mosState": 3,
#   "bmsSlave1.num": 1,
#   "bmsSlave1.openBmsIdx": 3,
#   "bmsSlave1.outputWatts": 216,
#   "bmsSlave1.remainCap": 15036,
#   "bmsSlave1.remainTime": 227,
#   "bmsSlave1.soc": 38,
#   "bmsSlave1.soh": 100,
#   "bmsSlave1.sysVer": 16843811,
#   "bmsSlave1.tagChgAmp": 32000,
#   "bmsSlave1.temp": 26,
#   "bmsSlave1.type": 1,
#   "bmsSlave1.vol": 53324,
#   "ems.bms0Online": 3,
#   "ems.bms1Online": 3,
#   "ems.bms2Online": 3,
#   "ems.bmsModel": 4,
#   "ems.bmsWarningState": 0,
#   "ems.chgAmp": 60000,
#   "ems.chgCmd": 1,
#   "ems.chgRemainTime": 5999,
#   "ems.chgState": 1,
#   "ems.chgVol": 54319,
#   "ems.dsgCmd": 1,
#   "ems.dsgRemainTime": 240,
#   "ems.emsIsNormalFlag": 1,
#   "ems.f32LcdShowSoc": 39.512756,
#   "ems.fanLevel": 0,
#   "ems.lcdShowSoc": 40,
#   "ems.maxAvailableNum": 2,
#   "ems.maxChargeSoc": 100,
#   "ems.maxCloseOilEbSoc": 100,
#   "ems.minDsgSoc": 15,
#   "ems.minOpenOilEbSoc": 0,
#   "ems.openBmsIdx": 3,
#   "ems.openUpsFlag": 1,
#   "ems.paraVolMax": 54402,
#   "ems.paraVolMin": 53302,
#   "inv.acDipSwitch": 2,
#   "inv.acInAmp": 0,
#   "inv.acInFreq": 0,
#   "inv.acInVol": 0,
#   "inv.acPassByAutoEn": 0,
#   "inv.cfgAcEnabled": 0,
#   "inv.cfgAcOutFreq": 1,
#   "inv.cfgAcOutVoltage": 230000,
#   "inv.cfgAcWorkMode": 0,
#   "inv.cfgAcXboost": 0,
#   "inv.cfgFastChgWatts": 2200,
#   "inv.cfgSlowChgWatts": 200,
#   "inv.cfgStandbyMin": 120,
#   "inv.chargerType": 0,
#   "inv.chgPauseFlag": 0,
#   "inv.dcInAmp": 0,
#   "inv.dcInTemp": 29,
#   "inv.dcInVol": 0,
#   "inv.dischargeType": 0,
#   "inv.errCode": 0,
#   "inv.fanState": 0,
#   "inv.inputWatts": 0,
#   "inv.invOutAmp": 0,
#   "inv.invOutFreq": 0,
#   "inv.invOutVol": 0,
#   "inv.invType": 8,
#   "inv.outputWatts": 0,
#   "inv.outTemp": 30,
#   "inv.sysVer": 16843557,
#   "kit.availableDataLen": 83,
#   "kit.maxKitNum": 2,
#   "kit.productInfoDetails": [
#     {
#       "appVersion": 16843811,
#       "curPower": -218,
#       "f32Soc": 38.360493,
#       "loaderVersion": 16843277,
#       "procedureState": 1,
#       "productDetail": 4,
#       "productType": 13,
#       "protocolAvaiFlag": 1,
#       "sn": "E2AB***********",
#       "soc": 38
#     },
#     {
#       "appVersion": 83886777,
#       "curPower": 435,
#       "f32Soc": 0,
#       "loaderVersion": 83886338,
#       "procedureState": 1,
#       "productDetail": 1,
#       "productType": 75,
#       "protocolAvaiFlag": 1,
#       "sn": "HW51************",
#       "soc": 0
#     }
#   ],
#   "kit.protocolVersion": 1,
#   "mppt.carOutAmp": 3,
#   "mppt.carOutVol": 0,
#   "mppt.carOutWatts": 0,
#   "mppt.carState": 0,
#   "mppt.carTemp": 0,
#   "mppt.cfgChgType": 0,
#   "mppt.cfgDcChgCurrent": 0,
#   "mppt.chgPauseFlag": 0,
#   "mppt.chgState": 0,
#   "mppt.chgType": 0,
#   "mppt.dc24vState": 0,
#   "mppt.dc24vTemp": 30,
#   "mppt.dcdc12vAmp": 0,
#   "mppt.dcdc12vVol": 0,
#   "mppt.dcdc12vWatts": 0,
#   "mppt.faultCode": 0,
#   "mppt.inAmp": 0,
#   "mppt.inVol": 1,
#   "mppt.inWatts": 0,
#   "mppt.mpptTemp": 30,
#   "mppt.outAmp": 2,
#   "mppt.outVol": 515,
#   "mppt.outWatts": 12,
#   "mppt.swVer": 50397726,
#   "mppt.xt60ChgType": 0,
#   "pd.beepState": 1,
#   "pd.carState": 0,
#   "pd.carTemp": 0,
#   "pd.carUsedTime": 3307,
#   "pd.carWatts": 0,
#   "pd.chgPowerAc": 97074,
#   "pd.chgPowerDc": 3,
#   "pd.chgSunPower": 0,
#   "pd.dcInUsedTime": 19,
#   "pd.dcOutState": 0,
#   "pd.dsgPowerAc": 1597,
#   "pd.dsgPowerDc": 278,
#   "pd.errCode": 0,
#   "pd.iconAcFreqMode": 1,
#   "pd.iconAcFreqState": 0,
#   "pd.iconBmsErrMode": 0,
#   "pd.iconBmsErrState": 0,
#   "pd.iconBmsParallelMode": 0,
#   "pd.iconBmsParallelState": 0,
#   "pd.iconBtMode": 0,
#   "pd.iconBtState": 0,
#   "pd.iconCarMode": 1,
#   "pd.iconCarState": 0,
#   "pd.iconChgStationMode": 0,
#   "pd.iconChgStationState": 0,
#   "pd.iconCoGasMode": 0,
#   "pd.iconCoGasState": 0,
#   "pd.iconEcoMode": 0,
#   "pd.iconEcoState": 0,
#   "pd.iconFactoryMode": 0,
#   "pd.iconFactoryState": 0,
#   "pd.iconFanMode": 0,
#   "pd.iconFanState": 0,
#   "pd.iconGasGenMode": 0,
#   "pd.iconGasGenState": 0,
#   "pd.iconHiTempMode": 0,
#   "pd.iconHiTempState": 0,
#   "pd.iconInvParallelMode": 0,
#   "pd.iconInvParallelState": 0,
#   "pd.iconLowTempMode": 0,
#   "pd.iconLowTempState": 0,
#   "pd.iconOverloadMode": 0,
#   "pd.iconOverloadState": 0,
#   "pd.iconPackHeaterMode": 0,
#   "pd.iconPackHeaterState": 0,
#   "pd.iconRcMode": 0,
#   "pd.iconRcState": 0,
#   "pd.iconRechgTimeMode": 0,
#   "pd.iconRechgTimeState": 0,
#   "pd.iconSocUpsMode": 0,
#   "pd.iconSocUpsState": 0,
#   "pd.iconSolarBracketMode": 0,
#   "pd.iconSolarBracketState": 0,
#   "pd.iconSolarPanelMode": 0,
#   "pd.iconSolarPanelState": 0,
#   "pd.iconTransSwMode": 0,
#   "pd.iconTransSwState": 0,
#   "pd.iconTypecMode": 0,
#   "pd.iconTypecState": 0,
#   "pd.iconUsbMode": 0,
#   "pd.iconUsbState": 0,
#   "pd.iconWifiMode": 0,
#   "pd.iconWifiState": 0,
#   "pd.iconWindGenMode": 0,
#   "pd.iconWindGenState": 0,
#   "pd.iconWirelessChgMode": 0,
#   "pd.iconWirelessChgState": 0,
#   "pd.invUsedTime": 476034,
#   "pd.kit0": 65,
#   "pd.kit1": 67,
#   "pd.kit2": 0,
#   "pd.lcdBrightness": 100,
#   "pd.lcdOffSec": 10,
#   "pd.model": 4,
#   "pd.mpptUsedTime": 0,
#   "pd.qcUsb1Watts": 0,
#   "pd.qcUsb2Watts": 0,
#   "pd.remainTime": 240,
#   "pd.soc": 41,
#   "pd.standByMode": 30,
#   "pd.sysChgDsgState": 1,
#   "pd.sysVer": 16844310,
#   "pd.typccUsedTime": 4642,
#   "pd.typec1Temp": 27,
#   "pd.typec1Watts": 0,
#   "pd.typec2Temp": 27,
#   "pd.typec2Watts": 0,
#   "pd.usb1Watts": 0,
#   "pd.usb2Watts": 0,
#   "pd.usbqcUsedTime": 13573,
#   "pd.usbUsedTime": 2545,
#   "pd.wattsInSum": 218,
#   "pd.wattsOutSum": 434,
#   "pd.wifiAutoRcvy": 0,
#   "pd.wifiRssi": 0,
#   "pd.wifiVer": 0,
#   "pd.wirelessWatts": 0
# }
