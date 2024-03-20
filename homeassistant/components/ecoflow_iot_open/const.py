"""Constants for the EcoFlow IoT Open integration."""

DOMAIN = "ecoflow_iot_open"
CONF_ACCESS_KEY = "access_key"
CONF_SECRET_KEY = "secret_key"

"""Define an EcoFlow equipment"""


class EcoFlowModel:
    """Define the equipment type by DeviceSN-prefix."""

    DELTA_MAX = "DAEB"  # productType = 13
    DELTA_MAX_SMART_EXTRA_BATTERY = "E2AB"  # productType=13
    POWERSTREAM = "HW51"  # productType=75
    SMART_PLUG = "HW52"
    SINGLE_AXIS_SOLAR_TRACKER = "HZ31"
