"""Services for HAIntercom."""
from homeassistant.core import HomeAssistant, ServiceCall
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, SERVICE_START_INTERCOM, SERVICE_STOP_INTERCOM, SERVICE_SEND_MESSAGE

SCHEMA_START_INTERCOM = vol.Schema({})
SCHEMA_STOP_INTERCOM = vol.Schema({})
SCHEMA_SEND_MESSAGE = vol.Schema({
    vol.Required("message"): cv.string,
})

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for HAIntercom integration."""
    async def handle_start_intercom(call: ServiceCall) -> None:
        """Handle start_intercom service."""
        entity = call.data.get("entity_id")
        await hass.services.async_call(DOMAIN, SERVICE_START_INTERCOM, {"entity_id": entity})

    async def handle_stop_intercom(call: ServiceCall) -> None:
        """Handle stop_intercom service."""
        entity = call.data.get("entity_id")
        await hass.services.async_call(DOMAIN, SERVICE_STOP_INTERCOM, {"entity_id": entity})

    async def handle_send_message(call: ServiceCall) -> None:
        """Handle send_message service."""
        entity = call.data.get("entity_id")
        message = call.data.get("message")
        await hass.services.async_call(DOMAIN, SERVICE_SEND_MESSAGE, {
            "entity_id": entity,
            "message": message,
        })

    hass.services.async_register(DOMAIN, SERVICE_START_INTERCOM, handle_start_intercom, SCHEMA_START_INTERCOM)
    hass.services.async_register(DOMAIN, SERVICE_STOP_INTERCOM, handle_stop_intercom, SCHEMA_STOP_INTERCOM)
    hass.services.async_register(DOMAIN, SERVICE_SEND_MESSAGE, handle_send_message, SCHEMA_SEND_MESSAGE)
