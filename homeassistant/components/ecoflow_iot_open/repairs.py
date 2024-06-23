"""Repairs implementation for EcoFlow IoT Open integration."""

from __future__ import annotations

from typing import cast

import voluptuous as vol

from homeassistant import data_entry_flow
from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.issue_registry import async_get as async_get_issue_registry

from .api import EcoFlowIoTOpenAPIInterface
from .const import API_CLIENT, DOMAIN


class EcoFlowIoTOpenRepairFlow(RepairsFlow):
    """Handler for an EcoFlow IoT Open issue."""

    _api: EcoFlowIoTOpenAPIInterface
    _config_entry: ConfigEntry

    def __init__(
        self, api: EcoFlowIoTOpenAPIInterface, config_entry: ConfigEntry
    ) -> None:
        """Create flow."""

        self._api = api
        self._config_entry = config_entry
        super().__init__()

    @callback
    def _async_get_placeholders(self) -> dict[str, str]:
        issue_registry = async_get_issue_registry(self.hass)
        description_placeholders = {}
        if issue := issue_registry.async_get_issue(self.handler, self.issue_id):
            description_placeholders = issue.translation_placeholders or {}
            if issue.learn_more_url:
                description_placeholders["learn_more"] = issue.learn_more_url

        return description_placeholders


class MqttConnectionIssueRepairFlow(EcoFlowIoTOpenRepairFlow):
    """Handler for a MQTT connection issue fixing flow."""

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the first step of MQTT connection fix flow."""

        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the confirm step of a MQTT connection fix flow."""
        if user_input is not None:
            await self._api.disconnect()
            await self._api.connect(self.hass, self._config_entry)
            return self.async_create_entry(title="", data={})

        placeholders = self._async_get_placeholders()
        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders=placeholders,
        )


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create EcoFlow IoT Open flow."""
    if data is not None and issue_id == DOMAIN + "_mqtt_connection":
        entry_id = cast(str, data["entry_id"])
        if (config_entry := hass.config_entries.async_get_entry(entry_id)) is not None:
            api: EcoFlowIoTOpenAPIInterface = hass.data[DOMAIN][API_CLIENT][
                config_entry.entry_id
            ]
            return MqttConnectionIssueRepairFlow(api, config_entry)
    return ConfirmRepairFlow()
