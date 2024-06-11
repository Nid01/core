"""EcoFlow Smart Plug."""

from collections.abc import Sequence

from homeassistant.components.sensor import SensorEntity

from ..api import EcoFlowIoTOpenDataHolder
from ..sensor import OutWattsSensorEntity
from . import BaseDevice


class SmartPlug(BaseDevice):
    """Smart Plug."""

    def __init__(self, device_info: dict, api_interface) -> None:
        """Initialize."""
        super().__init__(device_info, api_interface)
        self._model = "Smart Plug"

    def sensors(self, dataHolder: EcoFlowIoTOpenDataHolder) -> Sequence[SensorEntity]:
        """Available sensors for Smart Plug."""
        return [
            OutWattsSensorEntity(
                dataHolder=dataHolder,
                device=self,
                mqtt_key="iot.watts",
                title="watts",
            ),
        ]
