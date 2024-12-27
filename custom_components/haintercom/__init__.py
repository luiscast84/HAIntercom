# __init__.py
"""HAIntercom integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
  DOMAIN,
  CONF_DEVICES,
  CONF_REPLY_TIMEOUT,
  DEFAULT_REPLY_TIMEOUT,
)
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.MEDIA_PLAYER]

DEVICE_SCHEMA = vol.Schema({
  vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [cv.string]),
  vol.Optional(CONF_REPLY_TIMEOUT, default=DEFAULT_REPLY_TIMEOUT): cv.positive_int,
})

CONFIG_SCHEMA = vol.Schema(
  {DOMAIN: DEVICE_SCHEMA},
  extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
  """Set up HAIntercom integration."""
  if DOMAIN not in config:
      return True

  conf = config[DOMAIN]
  hass.data.setdefault(DOMAIN, {})
  hass.data[DOMAIN] = {
      CONF_DEVICES: conf[CONF_DEVICES],
      CONF_REPLY_TIMEOUT: conf.get(CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT),
  }
  
  await async_setup_services(hass)
  return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  """Set up from a config entry."""
  await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
  entry.async_on_unload(entry.add_update_listener(update_listener))
  await async_setup_services(hass)
  return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  """Unload a config entry."""
  unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
  if unload_ok:
      hass.data[DOMAIN].pop(entry.entry_id, None)
  return unload_ok

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
  """Update when config_entry options update."""
  await hass.config_entries.async_reload(entry.entry_id)