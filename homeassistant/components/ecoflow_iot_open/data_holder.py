"""The EcoFlow IoT Open integration."""

# from .products.powerstream import PowerStream
# from .products.single_axis_solar_tracker import SingleAxisSolarTracker
# from .products.smart_plug import SmartPlug
from datetime import datetime
import logging
from typing import Any

# from paho.mqtt import client as mqtt
from reactivex import Observable, Subject

from homeassistant.util import dt as dt_util

# from .products import BaseDevice

_LOGGER = logging.getLogger(__name__)


class EcoFlowIoTOpenDataHolder:
    """Data holder for the params of all available EcoFlow devices."""

    def __init__(self) -> None:
        """Initialize."""
        self.params = dict[str, dict[str, dict[str, Any]]]()
        self.__params_observable = Subject[dict[str, Any]]()

        self.__params_time = (
            dt_util.utcnow()
        )  # .replace(year=2000, month=1, day=1, hour=0, minute=0, second=0)

    def params_observable(self) -> Observable[dict[str, Any]]:
        """Return observable params."""
        return self.__params_observable

    def update_params(
        self,
        raw: dict[str, Any],
        # product: str,
        serial_number: str,
    ):
        """Update the device params."""
        # For devices like PowerStream and Single Axis Solar Tracker we receive "param" instead of "params"
        # if raw.get("param"):
        #     raw["params"] = raw["param"]

        # if raw.get("params"):
        # For devices like PowerStream and Single Axis Solar Tracker we receive the params values without prefix
        # if isinstance(raw.get("addr"), str):
        #     prefixed_params = {
        #         f"{raw.get("addr")}.{key}": value for key, value in raw.items()
        #     }
        #     raw = prefixed_params
        # if not self.params.get(product):
        #     self.params[product] = {}
        # if not self.params[product].get(serial_number):
        #     self.params[product][serial_number] = {}
        # self.params[product][serial_number].update(raw["params"])

        if not self.params.get(serial_number):
            self.params[serial_number] = {}
        self.params[serial_number].update(raw)
        self.__broadcast()
        # else:
        #     _LOGGER.error("Missing params in update dictionary: %s", raw)

    def __broadcast(self):
        """Broadcoast updated device params."""
        self.__params_observable.on_next(self.params)

    def params_time(self) -> datetime:
        """Return params time."""
        return self.__params_time
