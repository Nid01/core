"""Config flow for EcoFlow IoT Open integration."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError
import voluptuous as vol

from homeassistant.auth import InvalidAuthError
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import HomeAssistant, callback

from .api import EcoFlowIoTOpenAPIInterface
from .const import (
    CONF_ACCESS_KEY,
    CONF_BASE_URL,
    CONF_SECRET_KEY,
    CONF_SERVER_REGION,
    DEFAULT_AVAILABILITY_CHECK_INTERVAL_SEC,
    DESCRIPTION_ACCESS_KEY,
    DESCRIPTION_SECRET_KEY,
    DESCRIPTION_SERVER_REGION,
    DOMAIN,
    OPTS_AVAILABILITY_CHECK_INTERVAL_SEC,
)
from .errors import CannotConnect, InvalidCredentialsError

_LOGGER = logging.getLogger(__name__)

SERVER_CHOICES = ["EU", "US"]
DEFAULT_SERVER = "EU"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_KEY, description=DESCRIPTION_ACCESS_KEY): str,
        vol.Required(CONF_SECRET_KEY, description=DESCRIPTION_SECRET_KEY): str,
        vol.Required(
            CONF_SERVER_REGION,
            description=DESCRIPTION_SERVER_REGION,
        ): vol.In(SERVER_CHOICES),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    errors: dict[str, str] = {}

    if data[CONF_SERVER_REGION] == "EU":
        data[CONF_BASE_URL] = "https://api-e.ecoflow.com/iot-open"
    elif data[CONF_SERVER_REGION] == "US":
        data[CONF_BASE_URL] = "https://api-a.ecoflow.com/iot-open"
    else:
        errors[CONF_SERVER_REGION] = "invalid_server_region"
        return errors

    try:
        api = EcoFlowIoTOpenAPIInterface(
            hass,
            data[CONF_ACCESS_KEY],
            data[CONF_SECRET_KEY],
            data[CONF_BASE_URL],
        )
        await api.certification()

    except ClientError:
        _LOGGER.debug("Cannot connect", exc_info=True)
        errors["base"] = "cannot_connect"
    except InvalidCredentialsError:
        errors["base"] = "invalid_credentials"
    except Exception:  # pylint: disable=broad-except
        _LOGGER.exception("Unexpected exception", stack_info=True)
        errors["base"] = "unhandled"

    if errors:
        return errors

    return {"title": "EcoFlow IoT Open"}


class EcoFlowIoTOpenConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EcoFlow IoT Open."""

    VERSION = 1

    # TODO Extend config flow by adittional step for selecting specific devices after device list has been received from API. # pylint: disable=fixme

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
            except InvalidAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                options = {
                    OPTS_AVAILABILITY_CHECK_INTERVAL_SEC: DEFAULT_AVAILABILITY_CHECK_INTERVAL_SEC
                }

                return self.async_create_entry(
                    title=info["title"], data=user_input, options=options
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Options callback for EcoFlow IoT Open."""
        return EcoflowOptionsFlow(config_entry)


class EcoflowOptionsFlow(OptionsFlow):
    """Handle EcoFlow IoT Open options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize EcoFlow IoT Open options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            changed = self.hass.config_entries.async_update_entry(
                entry=self.config_entry,
                data=self.config_entry.data,
                options=user_input,
            )
            if changed:
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            last_step=True,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        OPTS_AVAILABILITY_CHECK_INTERVAL_SEC,
                        default=self.config_entry.options[
                            OPTS_AVAILABILITY_CHECK_INTERVAL_SEC
                        ],
                    ): int,
                }
            ),
        )
