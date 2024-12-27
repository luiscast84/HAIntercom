"""Services for HAIntercom."""
from homeassistant.core import HomeAssistant, ServiceCall
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.const import ATTR_ENTITY_ID

from .const import DOMAIN, SERVICE_START_INTERCOM, SERVICE_STOP_INTERCOM, SERVICE_SEND_MESSAGE

SCHEMA_START_INTERCOM = vol.Schema({
    vol.Optional("target_device"): cv.entity_id,
})

SCHEMA_STOP_INTERCOM = vol.Schema({})

SCHEMA_SEND_MESSAGE = vol.Schema({
    vol.Required("message"): cv.string,
    vol.Optional("target_device"): cv.entity_id,
})

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for HAIntercom integration."""
    async def handle_start_intercom(call: ServiceCall) -> None:
        """Handle start_intercom service."""
        target_entity_id = call.target["entity_id"][0]
        target_device = call.data.get("target_device")
        
        data = {"entity_id": target_entity_id}
        if target_device:
            data["target_device"] = target_device

        await hass.services.async_call(
            DOMAIN,
            "media_player",
            data,
            blocking=True
        )

    async def handle_stop_intercom(call: ServiceCall) -> None:
        """Handle stop_intercom service."""
        target_entity_id = call.target["entity_id"][0]
        await hass.services.async_call(
            DOMAIN,
            "media_player",
            {"entity_id": target_entity_id},
            blocking=True
        )

    async def handle_send_message(call: ServiceCall) -> None:
        """Handle send_message service."""
        target_entity_id = call.target["entity_id"][0]
        data = {
            "entity_id": target_entity_id,
            "message": call.data["message"]
        }
        if "target_device" in call.data:
            data["target_device"] = call.data["target_device"]

        await hass.services.async_call(
            DOMAIN,
            "media_player",
            data,
            blocking=True
        )

    hass.services.async_register(DOMAIN, SERVICE_START_INTERCOM, handle_start_intercom, schema=SCHEMA_START_INTERCOM)
    hass.services.async_register(DOMAIN, SERVICE_STOP_INTERCOM, handle_stop_intercom, schema=SCHEMA_STOP_INTERCOM)
    hass.services.async_register(DOMAIN, SERVICE_SEND_MESSAGE, handle_send_message, schema=SCHEMA_SEND_MESSAGE)