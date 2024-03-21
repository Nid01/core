"""Constants for the EcoFlow IoT Open integration."""

from enum import Enum
import logging

_LOGGER = logging.getLogger(__name__)


DOMAIN = "ecoflow_iot_open"
DATA = "data"

CONF_ACCESS_KEY = "access_key"
CONF_SECRET_KEY = "secret_key"

SIGNAL_ECOFLOW_IOT_OPEN_UPDATE_RECEIVED = "ecoflow_iot_open_update_received_{}_{}"

DELTA_MAX = "DAEB"  # productType = 13
# Potentially setup DELTA_MAX_SMART_EXTRA_BATTERY as separate device?
# DELTA_MAX_SMART_EXTRA_BATTERY = "E2AB"  # productType=13
POWERSTREAM = "HW51"  # productType=75
SMART_PLUG = "HW52"
SINGLE_AXIS_SOLAR_TRACKER = "HZ31"
# More SN-prefixes required


class EcoFlowProductType(Enum):
    """Define the equipment product type by DeviceSN-prefix."""

    DELTA_2 = 1
    RIVER_2 = 2
    RIVER_2_MAX = 3
    RIVER_2_PRO = 4
    DELTA_PRO = 5
    RIVER_MAX = 6
    RIVER_PRO = 7
    DELTA_MAX = 8  # productType = 13
    DELTA_2_MAX = 9  # productType = 81
    DELTA_MINI = 15  # productType = 15
    SINGLE_AXIS_SOLAR_TRACKER = 31
    WAVE_2 = 45  # productType = 45
    GLACIER = 46
    POWERSTREAM = 51
    SMART_PLUG = 52
    DIAGNOSTIC = 99


# class Equipment:
#     """Define a equipment."""

#     def __init__(self, equipment_info: dict) -> None:
#         """Create an EcoFlow equipment object."""
#         self._equipment_info = equipment_info

#     @staticmethod
#     def _coerce_type_from_string(value: str) -> EcoFlowProductType:
#         """Return a proper type from a string input."""
#         if value == DELTA_MAX:
#             return EcoFlowProductType.DELTA_MAX
#         elif value == POWERSTREAM:
#             return EcoFlowProductType.POWERSTREAM
#         elif value == SMART_PLUG:
#             return EcoFlowProductType.SMART_PLUG
#         elif value == SINGLE_AXIS_SOLAR_TRACKER:
#             return EcoFlowProductType.SINGLE_AXIS_SOLAR_TRACKER
#         else:
#             _LOGGER.error("Unknown equipment type state: %s", value)
#             return EcoFlowProductType.DIAGNOSTIC

#     @property
#     def serial_number(self) -> str:
#         """Return the equipment serial number."""
#         return self._equipment_info.get("serial_number")
