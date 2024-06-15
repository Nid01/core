"""Define package errors."""


class EcoFlowIoTOpenError(Exception):
    """Custom exception for EcoFlow IoT Open API errors."""


class InvalidCredentialsError(EcoFlowIoTOpenError):
    """Raised when invalid credentials are provided."""


class InvalidResponseFormat(EcoFlowIoTOpenError):
    """Raised when an invalid response format is received."""


class GenericHTTPError(EcoFlowIoTOpenError):
    """Generic HTTP error."""


class MqttError(EcoFlowIoTOpenError):
    """MQTT error."""


class ClientError(EcoFlowIoTOpenError):
    """Base class for client connection errors."""
