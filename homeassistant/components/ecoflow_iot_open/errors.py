"""Define package errors."""

from homeassistant.exceptions import HomeAssistantError


class EcoFlowIoTOpenError(HomeAssistantError):
    """Custom exception for EcoFlow IoT Open API errors."""


class CannotConnect(EcoFlowIoTOpenError):
    """Error to indicate we cannot connect."""


class DeviceNotAllowedError(EcoFlowIoTOpenError):
    """Response code 1006 indicates, that EcoFlow decided to block HTTP requests for the chosen device.

    Nesserary since EcoFlow decided to lock out devices which aren't officially supported from the iot "open" API (yet?).
    https://www.reddit.com/r/Ecoflow_community/comments/1lzp7qa/comment/n3e0tkn/
    """


class InvalidAuth(EcoFlowIoTOpenError):
    """Error to indicate there is invalid auth."""


class ClientError(EcoFlowIoTOpenError):
    """Base class for client connection errors."""


class GenericHTTPError(EcoFlowIoTOpenError):
    """Generic HTTP error."""


class InvalidCredentialsError(EcoFlowIoTOpenError):
    """Raised when invalid credentials are provided."""


class InvalidResponseFormat(EcoFlowIoTOpenError):
    """Raised when an invalid response format is received."""


class MqttError(EcoFlowIoTOpenError):
    """MQTT error."""
