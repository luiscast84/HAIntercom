"""HAIntercom integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.components import media_player
from homeassistant.config_entries import ConfigEntry, ConfigFlow 
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    Platform,
)
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
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

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [cv.string]),
                vol.Optional(CONF_REPLY_TIMEOUT, default=DEFAULT_REPLY_TIMEOUT): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up HAIntercom component."""
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
    """Set up HAIntercom from config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_services(hass)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok