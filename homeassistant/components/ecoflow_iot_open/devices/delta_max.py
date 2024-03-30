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

    @property
    def model(self) -> str:
        """Return the value 0-100? of the battery level."""
        return self._model
