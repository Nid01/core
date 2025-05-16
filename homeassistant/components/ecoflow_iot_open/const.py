"""Constants for the EcoFlow IoT Open integration."""

from enum import Enum

DOMAIN = "ecoflow_iot_open"
API_CLIENT = "api_client"
DATA_HOLDER = "data_holder"
PRODUCTS = "products"
DEVICES = "devices"
ECOFLOW = "EcoFlow"


CONF_OPEN_ACCESS_KEY = "accessKey"
DESCRIPTION_OPEN_ACCESS_KEY = "Enter your access key. Your credentials need to be generated at https://developer.ecoflow.com/"
CONF_OPEN_SECRET_KEY = "secretKey"
DESCRIPTION_OPEN_SECRET_KEY = "Enter your secret key. Your credentials need to be generated at https://developer.ecoflow.com/"
CONF_OPEN_SERVER_REGION = "open server region"
CONF_OPEN_BASE_URL = "base url"
DESCRIPTION_OPEN_SERVER_REGION = "Select the server region."

CONF_APP_USERNAME = "username"
DESCRIPTION_APP_USERNAME = "Enter your EcoFlow app username. This is the email address you use to log in to the EcoFlow app."
CONF_APP_PASSWORD = "password"
DESCRIPTION_APP_PASSWORD = "Enter your EcoFlow app password. This is the password you use to log in to the EcoFlow app."
CONF_APP_SERVER = "app server"
DESCRIPTION_APP_SERVER = "Enter the server for the EcoFlow app. This is usually api.ecoflow.com, but may be different for some users."


OPTS_AVAILABILITY_CHECK_INTERVAL_SEC = "availability_check_interval_sec"

DEFAULT_AVAILABILITY_CHECK_INTERVAL_SEC = 15


class ProductType(Enum):
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
    UNKNOWN = 100


SERIAL_NUMBER_PREFIXES = {
    ProductType.DELTA_MAX: "DAEB",  # productType = 13
    # Potentially setup DELTA_MAX_SMART_EXTRA_BATTERY as separate device?
    # ProductType.DELTA_MAX_SMART_EXTRA_BATTERY: "E2AB"  # productType=13
    ProductType.POWERSTREAM: "HW51",  # productType=75
    ProductType.SMART_PLUG: "HW52",
    ProductType.SINGLE_AXIS_SOLAR_TRACKER: "HZ31",
    # More SN-prefixes required
}
MODELS = {
    ProductType.DELTA_MAX: "DELTA Max",
    ProductType.POWERSTREAM: "PowerStream",
    ProductType.SMART_PLUG: "Smart Plug",
    ProductType.SINGLE_AXIS_SOLAR_TRACKER: "Single Axis Solar Tracker",
}

ATTR_STATUS_SN = "SN"
ATTR_STATUS_UPDATES = "status_request_count"
ATTR_STATUS_LAST_UPDATE = "status_last_update"
ATTR_STATUS_DATA_LAST_UPDATE = "data_last_update"
ATTR_STATUS_RECONNECTS = "reconnects"
ATTR_STATUS_PHASE = "status_phase"
