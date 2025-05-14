"""Config flow for EcoFlow IoT Open integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import HomeAssistant, callback

from .api import EcoFlowIoTOpenAPIInterface
from .const import (
    CONF_APP_PASSWORD,
    CONF_APP_SERVER,
    CONF_APP_USERNAME,
    CONF_OPEN_ACCESS_KEY,
    CONF_OPEN_BASE_URL,
    CONF_OPEN_SECRET_KEY,
    CONF_OPEN_SERVER_REGION,
    DEFAULT_AVAILABILITY_CHECK_INTERVAL_SEC,
    DESCRIPTION_APP_PASSWORD,
    DESCRIPTION_APP_SERVER,
    DESCRIPTION_APP_USERNAME,
    DESCRIPTION_OPEN_ACCESS_KEY,
    DESCRIPTION_OPEN_SECRET_KEY,
    DESCRIPTION_OPEN_SERVER_REGION,
    DOMAIN,
    OPTS_AVAILABILITY_CHECK_INTERVAL_SEC,
)
from .errors import ClientError, EcoFlowIoTOpenError, InvalidCredentialsError

_LOGGER = logging.getLogger(__name__)

OPEN_SERVER_CHOICES = ["EU", "US"]
OPEN_DEFAULT_SERVER = "EU"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_OPEN_ACCESS_KEY, description=DESCRIPTION_OPEN_ACCESS_KEY
        ): str,
        vol.Required(
            CONF_OPEN_SECRET_KEY, description=DESCRIPTION_OPEN_SECRET_KEY
        ): str,
        vol.Required(
            CONF_OPEN_SERVER_REGION,
            description=DESCRIPTION_OPEN_SERVER_REGION,
        ): vol.In(OPEN_SERVER_CHOICES),
        vol.Required(CONF_APP_USERNAME, description=DESCRIPTION_APP_USERNAME): str,
        vol.Required(CONF_APP_PASSWORD, description=DESCRIPTION_APP_PASSWORD): str,
        vol.Required(
            CONF_APP_SERVER,
            default="https://api.ecoflow.com",
            description=DESCRIPTION_APP_SERVER,
        ): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    errors: dict[str, str] = {}

    if data[CONF_OPEN_SERVER_REGION] == "EU":
        regional_url_part = "e"
    elif data[CONF_OPEN_SERVER_REGION] == "US":
        regional_url_part = "a"
    else:
        errors[CONF_OPEN_SERVER_REGION] = "invalid_server_region"
        return errors

    data[CONF_OPEN_BASE_URL] = f"https://api-{regional_url_part}.ecoflow.com/iot-open"

    try:
        api = EcoFlowIoTOpenAPIInterface(
            hass,
            data[CONF_OPEN_ACCESS_KEY],
            data[CONF_OPEN_SECRET_KEY],
            data[CONF_OPEN_BASE_URL],
            data[CONF_APP_USERNAME],
            data[CONF_APP_PASSWORD],
            data[CONF_APP_SERVER],
        )
        await api.certification()

    except ClientError:
        errors["base"] = "cannot_connect"
    except InvalidCredentialsError:
        errors["base"] = "invalid_credentials"
    except EcoFlowIoTOpenError as error:
        _LOGGER.exception("Unexpected exception")
        errors["base"] = f"unhandled error: {error.args}"

    if errors:
        return errors

    return {}


class EcoFlowIoTOpenConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EcoFlow IoT Open."""

    VERSION = 1

    # TODO Extend config flow by adittional step for selecting specific devices after device list has been received from API. # pylint: disable=fixme

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        self._async_abort_entries_match(
            {
                CONF_OPEN_ACCESS_KEY: user_input[CONF_OPEN_ACCESS_KEY],
                CONF_OPEN_SECRET_KEY: user_input[CONF_OPEN_SECRET_KEY],
                CONF_OPEN_SERVER_REGION: user_input[CONF_OPEN_SERVER_REGION],
                CONF_APP_USERNAME: user_input[CONF_APP_USERNAME],
                CONF_APP_PASSWORD: user_input[CONF_APP_PASSWORD],
                CONF_APP_SERVER: user_input[CONF_APP_SERVER],
            }
        )

        if not (errors := await validate_input(self.hass, user_input)):
            options = {
                OPTS_AVAILABILITY_CHECK_INTERVAL_SEC: DEFAULT_AVAILABILITY_CHECK_INTERVAL_SEC
            }
            return self.async_create_entry(
                title="EcoFlow IoT Open", data=user_input, options=options
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Options callback for EcoFlow IoT Open."""
        return EcoflowOptionsFlow()


class EcoflowOptionsFlow(OptionsFlow):
    """Handle EcoFlow IoT Open options."""

    def __init__(self) -> None:
        """Initialize EcoFlow IoT Open options flow."""

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
                self.hass.config_entries.async_schedule_reload(
                    self.config_entry.entry_id
                )
                return self.async_abort(
                    reason="Options submitted and config entry reloaded"
                )

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
