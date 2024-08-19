"""Define package errors."""

from homeassistant.exceptions import HomeAssistantError


class EcoFlowIoTOpenError(HomeAssistantError):
    """Custom exception for EcoFlow IoT Open API errors."""


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
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
