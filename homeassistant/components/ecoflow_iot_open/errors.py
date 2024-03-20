"""Define package errors."""


class EcoFlowIoTOpenError(Exception):
    """A base error."""


class InvalidCredentialsError(EcoFlowIoTOpenError):
    """An error related to invalid requests."""


class InvalidResponseFormat(EcoFlowIoTOpenError):
    """An error related to invalid requests."""


class GenericHTTPError(EcoFlowIoTOpenError):
    """An error related to invalid requests."""
