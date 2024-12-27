"""Config flow for Home Assistant Intercom integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN

from .const import DOMAIN, CONF_DEVICES, CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT

class IntercomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Home Assistant Intercom."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Home Assistant Intercom",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICES): str,
                vol.Optional(CONF_REPLY_TIMEOUT, default=DEFAULT_REPLY_TIMEOUT): int,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return IntercomOptionsFlow(config_entry)