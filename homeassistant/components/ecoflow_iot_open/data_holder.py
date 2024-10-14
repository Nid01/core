"""The EcoFlow IoT Open integration."""

import logging
from typing import Any

from reactivex import Observable, Subject

_LOGGER = logging.getLogger(__name__)


class EcoFlowIoTOpenDataHolder:
    """Data holder for the params of all available EcoFlow devices."""

    def __init__(self) -> None:
        """Initialize."""
        self.params = dict[str, dict[str, dict[str, Any]]]()
        self.__params_observable = Subject[dict[str, Any]]()

    def params_observable(self) -> Observable[dict[str, Any]]:
        """Return observable params."""
        return self.__params_observable

    def update_params(
        self,
        raw: dict[str, Any],
        serial_number: str,
    ):
        """Update the device params."""

        if not self.params.get(serial_number):
            self.params[serial_number] = {}
        self.params[serial_number].update(raw)
        self.__broadcast()

    def __broadcast(self):
        """Broadcoast updated device params."""
        self.__params_observable.on_next(self.params)
