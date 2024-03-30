"""Define package errors."""


class EcoFlowIoTOpenError(Exception):
    """EcoFlow IoT Open error."""


class InvalidCredentialsError(EcoFlowIoTOpenError):
    """Invalid credentials error."""


class InvalidResponseFormat(EcoFlowIoTOpenError):
    """Invalid response format error."""


class GenericHTTPError(EcoFlowIoTOpenError):
    """Generic HTTP error."""


class MqttError(EcoFlowIoTOpenError):
    """MQTT error."""


class ClientError(EcoFlowIoTOpenError):
    """Base class for client connection errors."""
