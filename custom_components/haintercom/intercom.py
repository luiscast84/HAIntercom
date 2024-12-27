"""Intercom implementation for Home Assistant."""
import asyncio
import logging
import voluptuous as vol
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
)
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    SUPPORT_PLAY_MEDIA,
    SUPPORT_VOLUME_SET,
)
from homeassistant.components.media_player.const import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent

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

class HAIntercom(MediaPlayerEntity):
    """Representation of an Intercom instance."""

    def __init__(self, hass: HomeAssistant, name: str, devices: list, reply_timeout: int):
        """Initialize the intercom."""
        self.hass = hass
        self._name = name
        self._devices = devices
        self._reply_timeout = reply_timeout
        self._state = "idle"
        self._active_session = False
        self._current_speaker = None
        self._reply_timer = None

    @property
    def name(self):
        """Return the name of the intercom."""
        return self._name

    @property
    def state(self):
        """Return the state of the intercom."""
        return self._state

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_PLAY_MEDIA | SUPPORT_VOLUME_SET

    async def async_start_session(self, target_device=None):
        """Start an intercom session."""
        if self._active_session:
            return

        self._active_session = True
        self._state = "active"
        self._current_speaker = target_device

        # Notify devices
        await self._notify_devices("Intercom session started")
        
        # Start reply timeout
        if self._reply_timer:
            self._reply_timer.cancel()
        self._reply_timer = asyncio.create_task(self._handle_reply_timeout())

    async def async_stop_session(self):
        """Stop the intercom session."""
        if not self._active_session:
            return

        self._active_session = False
        self._state = "idle"
        self._current_speaker = None

        if self._reply_timer:
            self._reply_timer.cancel()
            self._reply_timer = None

        await self._notify_devices("Intercom session ended")

    async def async_send_message(self, message: str, target_device=None):
        """Send a message through the intercom."""
        if not self._active_session:
            await self.async_start_session(target_device)

        # Send message to target device(s)
        devices = [target_device] if target_device else self._devices
        for device in devices:
            await self.hass.services.async_call(
                "tts",
                "google_translate_say",
                {
                    "entity_id": device,
                    "message": message,
                },
            )

        # Reset reply timer
        if self._reply_timer:
            self._reply_timer.cancel()
        self._reply_timer = asyncio.create_task(self._handle_reply_timeout())

    async def _handle_reply_timeout(self):
        """Handle reply timeout."""
        await asyncio.sleep(self._reply_timeout)
        await self.async_stop_session()

    async def _notify_devices(self, message: str):
        """Send notification to all devices."""
        for device in self._devices:
            await self.hass.services.async_call(
                "tts",
                "google_translate_say",
                {
                    "entity_id": device,
                    "message": message,
                },
            )

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Intercom platform."""
    devices = config.get(CONF_DEVICES)
    reply_timeout = config.get(CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT)

    intercom = HAIntercom(hass, "Home Assistant Intercom", devices, reply_timeout)
    async_add_entities([intercom])

    # Register services
    component = EntityComponent(_LOGGER, DOMAIN, hass)

    hass.services.async_register(
        DOMAIN,
        SERVICE_START_INTERCOM,
        intercom.async_start_session,
        schema=vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_INTERCOM,
        intercom.async_stop_session,
        schema=vol.Schema({}),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_MESSAGE,
        intercom.async_send_message,
        schema=vol.Schema({
            vol.Required("message"): cv.string,
            vol.Optional(ATTR_ENTITY_ID): cv.entity_id,
        }),
    )

    return True