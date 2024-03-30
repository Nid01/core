"""Config flow for EcoFlow IoT Open integration."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .api import EcoFlowIoTOpenAPIInterface
from .const import CONF_ACCESS_KEY, CONF_SECRET_KEY, DOMAIN
from .errors import InvalidCredentialsError

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need # pylint: disable=fixme
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        # vol.Required(CONF_HOST): str,
        vol.Required(CONF_ACCESS_KEY): str,
        vol.Required(CONF_SECRET_KEY): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection. # pylint: disable=fixme

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )
    errors: dict[str, str] = {}

    try:
        await EcoFlowIoTOpenAPIInterface.certification(
            data[CONF_ACCESS_KEY], data[CONF_SECRET_KEY]
        )

    except ClientError:
        _LOGGER.debug("Cannot connect", exc_info=True)
        errors["base"] = "cannot_connect"
    except InvalidCredentialsError:
        errors["base"] = "invalid_credentials"
    except Exception:  # pylint: disable=broad-except
        _LOGGER.exception("Unexpected exception during login", stack_info=True)
        errors["base"] = "unknown"

    if errors:
        return errors

    return {"title": "EcoFlow IoT Open"}


class EcoFlowIoTOpenConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EcoFlow IoT Open."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
