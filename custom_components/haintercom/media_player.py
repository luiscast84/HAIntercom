"""Media player platform for HAIntercom."""
from __future__ import annotations

import logging
import asyncio
from typing import Any

import voluptuous as vol

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    CONF_DEVICES,
    CONF_REPLY_TIMEOUT,
    DEFAULT_REPLY_TIMEOUT,
    SERVICE_START_INTERCOM,
    SERVICE_STOP_INTERCOM,
    SERVICE_SEND_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HAIntercom media player from config entry."""
    devices = config_entry.data[CONF_DEVICES].split(",")
    reply_timeout = config_entry.data.get(CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT)

    entities = []
    for device in devices:
        entities.append(HAIntercomMediaPlayer(hass, device.strip(), reply_timeout))

    async_add_entities(entities)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_START_INTERCOM,
        {},
        "async_start_intercom",
    )

    platform.async_register_entity_service(
        SERVICE_STOP_INTERCOM,
        {},
        "async_stop_intercom",
    )

    platform.async_register_entity_service(
        SERVICE_SEND_MESSAGE,
        {
            vol.Required("message"): cv.string,
        },
        "async_send_message",
    )

class HAIntercomMediaPlayer(MediaPlayerEntity):
    """Representation of a HAIntercom media player."""

    def __init__(self, hass: HomeAssistant, device_id: str, reply_timeout: int) -> None:
        """Initialize the media player."""
        self.hass = hass
        self._device_id = device_id
        self._reply_timeout = reply_timeout
        self._state = MediaPlayerState.IDLE
        self._volume = 0.5
        self._available = True
        self._active_session = False
        self._attr_unique_id = f"{DOMAIN}_{device_id}"
        self._attr_name = f"Intercom {device_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._attr_name,
            manufacturer="Home Assistant Community",
            model="Intercom",
        )

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        return self._state

    @property
    def volume_level(self) -> float:
        """Return the volume level."""
        return self._volume

    @property
    def supported_features(self) -> int:
        """Flag media player features that are supported."""
        return MediaPlayerEntityFeature.VOLUME_SET | MediaPlayerEntityFeature.PLAY_MEDIA

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level."""
        self._volume = volume

    async def async_start_intercom(self) -> None:
        """Start intercom session."""
        if self._active_session:
            return

        self._active_session = True
        self._state = MediaPlayerState.PLAYING
        await self.async_play_media("announce", "Intercom session started")

    async def async_stop_intercom(self) -> None:
        """Stop intercom session."""
        if not self._active_session:
            return

        self._active_session = False
        self._state = MediaPlayerState.IDLE
        await self.async_play_media("announce", "Intercom session ended")

    async def async_send_message(self, message: str) -> None:
        """Send message through intercom."""
        if not self._active_session:
            await self.async_start_intercom()

        self._state = MediaPlayerState.PLAYING
        await self.async_play_media("announce", message)
        await asyncio.sleep(len(message) * 0.1)
        self._state = MediaPlayerState.IDLE
        self.async_write_ha_state()

    async def async_play_media(
        self, media_type: str, media_id: str, **kwargs: Any
    ) -> None:
        """Play media."""
        if media_type != "announce":
            _LOGGER.error("Invalid media type %s. Only 'announce' is supported", media_type)
            return

        await self.hass.services.async_call(
            "tts",
            "google_translate_say",
            {
                "entity_id": self._device_id,
                "message": media_id,
            },
            blocking=True,
        )