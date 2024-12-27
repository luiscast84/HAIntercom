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

# Manufacturers
MANUFACTURER = "Home Assistant Community"
MODEL = "Intercom"