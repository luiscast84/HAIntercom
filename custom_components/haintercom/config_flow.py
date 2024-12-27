# config_flow.py
"""Config flow for HAIntercom."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_NAME

from .const import (
   DOMAIN,
   CONF_DEVICES,
   CONF_REPLY_TIMEOUT,
   DEFAULT_REPLY_TIMEOUT,
)

class HAIntercomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
   """Handle a config flow for HAIntercom."""

   VERSION = 1
   CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

   async def async_step_user(
       self, user_input: dict[str, Any] | None = None
   ) -> FlowResult:
       """Handle the initial step."""
       errors = {}

       if user_input is not None:
           await self.async_set_unique_id(user_input[CONF_NAME])
           self._abort_if_unique_id_configured()
           
           return self.async_create_entry(
               title=user_input[CONF_NAME],
               data=user_input,
           )

       data_schema = vol.Schema({
           vol.Required(CONF_NAME): str,
           vol.Required(CONF_DEVICES): str,
           vol.Optional(CONF_REPLY_TIMEOUT, default=DEFAULT_REPLY_TIMEOUT): int,
       })

       return self.async_show_form(
           step_id="user",
           data_schema=data_schema,
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

       options_schema = vol.Schema({
           vol.Required(CONF_DEVICES, 
               default=self.config_entry.data.get(CONF_DEVICES, "")): str,
           vol.Optional(CONF_REPLY_TIMEOUT,
               default=self.config_entry.data.get(
                   CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT
               )): int,
       })

       return self.async_show_form(
           step_id="init",
           data_schema=options_schema,
       )