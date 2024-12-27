# __init__.py
"""HAIntercom integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.MEDIA_PLAYER]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
   """Set up HAIntercom integration."""
   hass.data.setdefault(DOMAIN, {})
   return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
   """Set up from a config entry."""
   await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
   entry.async_on_unload(entry.add_update_listener(update_listener))
   return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
   """Unload a config entry."""
   return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
   """Update when config_entry options update."""
   await hass.config_entries.async_reload(entry.entry_id)

# const.py
"""Constants for HAIntercom."""
from typing import Final

DOMAIN: Final = "haintercom"
CONF_DEVICES = "devices"
CONF_REPLY_TIMEOUT = "reply_timeout"
DEFAULT_REPLY_TIMEOUT = 60

# Service names
SERVICE_START_INTERCOM = "start_intercom"
SERVICE_STOP_INTERCOM = "stop_intercom"
SERVICE_SEND_MESSAGE = "send_message"

# States
STATE_IDLE = "idle"
STATE_PLAYING = "playing"

# config_flow.py
"""Config flow for HAIntercom."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_NAME

from .const import DOMAIN, CONF_DEVICES, CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT

class HAIntercomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
   """Handle a config flow for HAIntercom."""

   VERSION = 1

   async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
       """Handle the initial step."""
       errors = {}

       if user_input is not None:
           await self.async_set_unique_id(user_input[CONF_NAME])
           self._abort_if_unique_id_configured()
           
           return self.async_create_entry(
               title=user_input[CONF_NAME],
               data=user_input,
           )

       return self.async_show_form(
           step_id="user",
           data_schema=vol.Schema({
               vol.Required(CONF_NAME): str,
               vol.Required(CONF_DEVICES): str,
               vol.Optional(CONF_REPLY_TIMEOUT, default=DEFAULT_REPLY_TIMEOUT): int,
           }),
           errors=errors,
       )

   @staticmethod
   @callback
   def async_get_options_flow(
       config_entry: config_entries.ConfigEntry,
   ) -> HAIntercomOptionsFlow:
       """Create the options flow."""
       return HAIntercomOptionsFlow(config_entry)

class HAIntercomOptionsFlow(config_entries.OptionsFlow):
   """HAIntercom config flow options handler."""

   def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
       """Initialize options flow."""
       self.config_entry = config_entry

   async def async_step_init(
       self, user_input: dict[str, Any] | None = None
   ) -> FlowResult:
       """Manage options."""
       if user_input is not None:
           return self.async_create_entry(title="", data=user_input)

       return self.async_show_form(
           step_id="init",
           data_schema=vol.Schema(
               {
                   vol.Required(
                       CONF_DEVICES,
                       default=self.config_entry.data.get(CONF_DEVICES, ""),
                   ): str,
                   vol.Optional(
                       CONF_REPLY_TIMEOUT,
                       default=self.config_entry.data.get(
                           CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT
                       ),
                   ): int,
               }
           ),
       )