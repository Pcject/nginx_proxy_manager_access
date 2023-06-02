"""The Nginx Proxy Manager Access integration."""
from __future__ import annotations

from async_timeout import timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, Config
from homeassistant.exceptions import ConfigEntryNotReady
from .helpers import setup_client
from .client import LoginRequired, LoginFailed
from requests.exceptions import RequestException


from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWD,
    CONF_HOST,
    CONF_VERIFY_SSL,
    CONF_CACHE_SECONDS,
)
import logging
_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH]


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured nginx proxy manager."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nginx Proxy Manager Access from a config entry."""
    
    try:
        hass.data[DOMAIN][entry.entry_id] = await hass.async_add_executor_job(
            setup_client,
            entry.data[CONF_HOST],
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWD],
            entry.data[CONF_VERIFY_SSL],
            entry.data[CONF_CACHE_SECONDS],
        )
    except LoginRequired as err:
        _LOGGER.error("LoginRequired")
        raise ConfigEntryNotReady from err
    except LoginFailed as err:
        _LOGGER.error("Invalid credentials")
        raise ConfigEntryNotReady from err
    except RequestException as err:
        _LOGGER.error("Failed to connect")
        raise ConfigEntryNotReady from err
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Nginx Proxy Manager Access config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN][entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
    return unload_ok
