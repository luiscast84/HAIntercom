from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
    devices = config_entry.data[CONF_DEVICES].split(",")
    reply_timeout = config_entry.data.get(CONF_REPLY_TIMEOUT, DEFAULT_REPLY_TIMEOUT)
    entities = []
    for device in devices:
        entities.append(HAIntercomMediaPlayer(hass, device.strip(), reply_timeout))
    async_add_entities(entities)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("entities", []).extend(entities)

class HAIntercomMediaPlayer(MediaPlayerEntity):
    def __init__(self, hass: HomeAssistant, device_id: str, reply_timeout: int) -> None:
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
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._attr_name,
            manufacturer="Home Assistant Community",
            model="Intercom",
        )

    @property
    def state(self) -> MediaPlayerState:
        return self._state

    @property
    def volume_level(self) -> float:
        return self._volume

    @property
    def supported_features(self) -> int:
        return MediaPlayerEntityFeature.VOLUME_SET | MediaPlayerEntityFeature.PLAY_MEDIA

    @property
    def available(self) -> bool:
        return self._available

    async def async_set_volume_level(self, volume: float) -> None:
        self._volume = volume

    async def async_start_intercom(self, target_device=None) -> None:
        if self._active_session:
            return
        self._active_session = True
        self._state = MediaPlayerState.PLAYING
        await self.async_play_media("announce", "Intercom session started", target_device)

    async def async_stop_intercom(self) -> None:
        if not self._active_session:
            return
        self._active_session = False
        self._state = MediaPlayerState.IDLE
        await self.async_play_media("announce", "Intercom session ended")

    async def async_send_message(self, message: str, target_device=None) -> None:
        if not self._active_session:
            await self.async_start_intercom(target_device)
        self._state = MediaPlayerState.PLAYING
        await self.async_play_media("announce", message, target_device)
        await asyncio.sleep(len(message) * 0.1)
        self._state = MediaPlayerState.IDLE
        self.async_write_ha_state()

    async def async_play_media(
        self, media_type: str, media_id: str, target_device=None
    ) -> None:
        if media_type != "announce":
            _LOGGER.error("Invalid media type %s. Only 'announce' is supported", media_type)
            return
        if target_device:
            entity_ids = [target_device]
        else:
            entity_ids = [self._device_id]
        for entity_id in entity_ids:
            await self.hass.services.async_call(
                "tts",
                "google_translate_say",
                {
                    "entity_id": entity_id,
                    "message": media_id,
                },
                blocking=True,
            )