"""EcoFlow PowerStream."""

from collections.abc import Sequence

from homeassistant.components.sensor import SensorEntity

from ..api import EcoFlowIoTOpenDataHolder
from ..sensor import (
    AmpSensorEntity,
    BrightnessSensorEntity,
    CountSensorEntity,
    DeciwattsSensorEntity,
    FrequencySensorEntity,
    LevelSensorEntity,
    MiscSensorEntity,
    RemainingTimeSensorEntity,
    StatusSensorEntity,
    TempSensorEntity,
    VoltSensorEntity,
)
from . import BaseDevice


class PowerStream(BaseDevice):
    """PowerStream."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "PowerStream"

    def sensors(self, dataHolder: EcoFlowIoTOpenDataHolder) -> Sequence[SensorEntity]:
        """Available sensors for PowerStream."""
        return [
            # Counter
            CountSensorEntity(dataHolder, self, "iot.resetCount"),
            # Wattage
            DeciwattsSensorEntity(
                dataHolder=dataHolder, device=self, mqtt_key="iot.invOutputWatts"
            ),
            DeciwattsSensorEntity(dataHolder, self, "iot.batInputWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.batErrorInvLoadLimit"),
            DeciwattsSensorEntity(dataHolder, self, "iot.batOutputLoadLimit"),
            DeciwattsSensorEntity(dataHolder, self, "iot.consWatt"),
            DeciwattsSensorEntity(dataHolder, self, "iot.dynamicWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.floadLimitOut"),
            DeciwattsSensorEntity(dataHolder, self, "iot.geneWatt"),
            DeciwattsSensorEntity(dataHolder, self, "iot.gridConsWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.invDemandWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.invOutputLoadLimit"),
            DeciwattsSensorEntity(dataHolder, self, "iot.invToOtherWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.invToPlugWatts"),
            # DeciwattsSensorEntity(dataHolder, self, "iot.lowerLimit"), # value of 100 doesn't seem to be a valid wattage
            DeciwattsSensorEntity(dataHolder, self, "iot.permanentWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.plugTotalWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.pv1InputWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.pv2InputWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.pvPowerLimitAcPower"),
            DeciwattsSensorEntity(dataHolder, self, "iot.pvToInvWatts"),
            DeciwattsSensorEntity(dataHolder, self, "iot.ratedPower"),
            DeciwattsSensorEntity(dataHolder, self, "iot.spaceDemandWatts"),
            # DeciwattsSensorEntity(dataHolder, self, "iot.upperLimit"), # value of 100 doesn't seem to be wattage
            # Level
            LevelSensorEntity(
                dataHolder=dataHolder, device=self, mqtt_key="iot.batSoc"
            ),
            # Current
            AmpSensorEntity(dataHolder, self, "iot.batInputCur"),
            AmpSensorEntity(dataHolder, self, "iot.bmsReqChgAmp"),
            AmpSensorEntity(dataHolder, self, "iot.invOutputCur"),
            AmpSensorEntity(dataHolder, self, "iot.pv1InputCur"),
            AmpSensorEntity(dataHolder, self, "iot.pv2InputCur"),
            # Frequency
            FrequencySensorEntity(dataHolder, self, "iot.invFreq"),
            # Voltage
            VoltSensorEntity(dataHolder, self, "iot.batInputVolt"),
            VoltSensorEntity(dataHolder, self, "iot.batOpVolt"),
            VoltSensorEntity(dataHolder, self, "iot.invInputVolt"),
            VoltSensorEntity(dataHolder, self, "iot.invOpVolt"),
            VoltSensorEntity(dataHolder, self, "iot.llcInputVolt"),
            VoltSensorEntity(dataHolder, self, "iot.llcOpVolt"),
            VoltSensorEntity(dataHolder, self, "iot.pv1InputVolt"),
            VoltSensorEntity(dataHolder, self, "iot.pv1OpVolt"),
            VoltSensorEntity(dataHolder, self, "iot.pv2InputVolt"),
            VoltSensorEntity(dataHolder, self, "iot.pv2OpVolt"),
            # Miscellaneous
            MiscSensorEntity(dataHolder, self, "iot.acOffFlag"),
            MiscSensorEntity(dataHolder, self, "iot.antiBackFlowFlag"),
            MiscSensorEntity(dataHolder, self, "iot.batErrCode"),
            MiscSensorEntity(dataHolder, self, "iot.batLoadLimitFlag"),
            MiscSensorEntity(dataHolder, self, "iot.batOffFlag"),
            MiscSensorEntity(dataHolder, self, "iot.batStatue"),
            MiscSensorEntity(dataHolder, self, "iot.batSystem"),
            MiscSensorEntity(dataHolder, self, "iot.batWarningCode"),
            # MiscSensorEntity(dataHolder, self, "iot.bmsReqChgVol"),  # Values doesn't seem to be voltage
            MiscSensorEntity(dataHolder, self, "iot.bpType"),
            MiscSensorEntity(dataHolder, self, "iot.consNum"),
            MiscSensorEntity(dataHolder, self, "iot.feedProtect"),
            MiscSensorEntity(dataHolder, self, "iot.geneNum"),
            MiscSensorEntity(dataHolder, self, "iot.heartbeatFrequency"),
            MiscSensorEntity(dataHolder, self, "iot.installCountry"),
            MiscSensorEntity(dataHolder, self, "iot.installTown"),
            MiscSensorEntity(dataHolder, self, "iot.interfaceConnFlag"),
            BrightnessSensorEntity(dataHolder, self, "iot.invBrightness"),
            MiscSensorEntity(dataHolder, self, "iot.invErrCode"),
            MiscSensorEntity(dataHolder, self, "iot.invLoadLimitFlag"),
            MiscSensorEntity(dataHolder, self, "iot.invOnOff"),
            MiscSensorEntity(dataHolder, self, "iot.invRelayStatus"),
            MiscSensorEntity(dataHolder, self, "iot.invStatue"),
            MiscSensorEntity(dataHolder, self, "iot.invWarnCode"),
            MiscSensorEntity(dataHolder, self, "iot.llcErrCode"),
            MiscSensorEntity(dataHolder, self, "iot.llcOffFlag"),
            MiscSensorEntity(dataHolder, self, "iot.llcStatue"),
            MiscSensorEntity(dataHolder, self, "iot.llcWarningCode"),
            MiscSensorEntity(dataHolder, self, "iot.meshId"),
            MiscSensorEntity(dataHolder, self, "iot.meshLayel"),
            MiscSensorEntity(dataHolder, self, "iot.mqttErr"),
            MiscSensorEntity(dataHolder, self, "iot.parentMac"),
            MiscSensorEntity(dataHolder, self, "iot.pv1CtrlMpptOffFlag"),
            MiscSensorEntity(dataHolder, self, "iot.pv1ErrCode"),
            MiscSensorEntity(dataHolder, self, "iot.pv1RelayStatus"),
            MiscSensorEntity(dataHolder, self, "iot.pv1Statue"),
            MiscSensorEntity(dataHolder, self, "iot.pv1WarnCode"),
            MiscSensorEntity(dataHolder, self, "iot.pv2CtrlMpptOffFlag"),
            MiscSensorEntity(dataHolder, self, "iot.pv2ErrCode"),
            MiscSensorEntity(dataHolder, self, "iot.pv2RelayStatus"),
            MiscSensorEntity(dataHolder, self, "iot.pv2Statue"),
            MiscSensorEntity(dataHolder, self, "iot.pv2WarningCode"),
            MiscSensorEntity(dataHolder, self, "iot.resetReason"),
            MiscSensorEntity(dataHolder, self, "iot.selfMac"),
            MiscSensorEntity(dataHolder, self, "iot.staIpAddr"),
            MiscSensorEntity(dataHolder, self, "iot.supplyPriority"),
            MiscSensorEntity(dataHolder, self, "iot.uwloadLimitFlag"),
            MiscSensorEntity(dataHolder, self, "iot.uwlowLightFlag"),
            MiscSensorEntity(dataHolder, self, "iot.uwsocFlag"),
            MiscSensorEntity(dataHolder, self, "iot.wifiErr"),
            MiscSensorEntity(dataHolder, self, "iot.wifiRssi"),
            MiscSensorEntity(dataHolder, self, "iot.wirelessErrCode"),
            MiscSensorEntity(dataHolder, self, "iot.wirelessWarnCode"),
            # Temperature
            TempSensorEntity(dataHolder, self, "iot.batTemp", factor=10),
            TempSensorEntity(dataHolder, self, "iot.invTemp", factor=10),
            TempSensorEntity(dataHolder, self, "iot.llcTemp", factor=10),
            TempSensorEntity(dataHolder, self, "iot.pv1Temp", factor=10),
            TempSensorEntity(dataHolder, self, "iot.pv2Temp", factor=10),
            # Time
            RemainingTimeSensorEntity(dataHolder, self, "iot.chgRemainTime"),
            RemainingTimeSensorEntity(dataHolder, self, "iot.dsgRemainTime"),
            # Status
            StatusSensorEntity(dataHolder, self),
        ]

    # def datetimes(...)..
    # DateTimeEntity(dataHolder, self, "iot.updateTime"),
    # DateTimeEntity(dataHolder, self, "iot.wifiErrTime"), # Parse integer value as datetime?
    # MiscSensorEntity(dataHolder, self, "iot.mqttErrTime"), # Parse integer value as datetime?
