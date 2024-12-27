"""Constants for the Home Assistant Intercom integration."""
DOMAIN = "haintercom"
CONF_DEVICES = "devices"
CONF_REPLY_TIMEOUT = "reply_timeout"

DEFAULT_REPLY_TIMEOUT = 60

SERVICE_START_INTERCOM = "start_intercom"
SERVICE_STOP_INTERCOM = "stop_intercom"
SERVICE_SEND_MESSAGE = "send_message"