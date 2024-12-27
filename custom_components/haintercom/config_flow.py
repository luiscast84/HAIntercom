"""Config flow for HAIntercom."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_DEVICES, CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT

class HAIntercomConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HAIntercom."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_DEVICES): str,
                    vol.Optional(
                        CONF_REPLY_TIMEOUT, default=DEFAULT_REPLY_TIMEOUT
                    ): int,
                }
            ),
            errors=errors,
        )
