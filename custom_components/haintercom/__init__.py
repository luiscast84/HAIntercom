from __future__ import annotations
import logging
import voluptuous as vol
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from .const import (
    DOMAIN,
    CONF_DEVICES,
    CONF_REPLY_TIMEOUT,
    DEFAULT_REPLY_TIMEOUT,
    SERVICE_START_INTERCOM,
    SERVICE_STOP_INTERCOM,
    SERVICE_SEND_MESSAGE,
)
from .media_player import async_setup_entry as media_player_setup

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
    if DOMAIN not in config:
        return True
    conf = config[DOMAIN]
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = {
        CONF_DEVICES: conf[CONF_DEVICES],
        CONF_REPLY_TIMEOUT: conf.get(CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT),
    }
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await media_player_setup(hass, entry)
    entities = hass.data[DOMAIN].get("entities", [])
    async def async_handle_start_intercom(call):
        entity_ids = call.data.get("entity_id")
        target_device = call.data.get("target_device")
        for entity in entities:
            if entity.entity_id in entity_ids:
                await entity.async_start_intercom(target_device)
    async def async_handle_stop_intercom(call):
        entity_ids = call.data.get("entity_id")
        for entity in entities:
            if entity.entity_id in entity_ids:
                await entity.async_stop_intercom()
    async def async_handle_send_message(call):
        entity_ids = call.data.get("entity_id")
        message = call.data.get("message")
        target_device = call.data.get("target_device")
        for entity in entities:
            if entity.entity_id in entity_ids:
                await entity.async_send_message(message, target_device)
    hass.services.async_register(
        DOMAIN,
        SERVICE_START_INTERCOM,
        async_handle_start_intercom,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_ids,
                vol.Optional("target_device"): cv.entity_id,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_INTERCOM,
        async_handle_stop_intercom,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_ids,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_MESSAGE,
        async_handle_send_message,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_ids,
                vol.Required("message"): cv.string,
                vol.Optional("target_device"): cv.entity_id,
            }
        ),
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)