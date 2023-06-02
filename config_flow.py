"""Config flow for Nginx Proxy Manager Access integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from .helpers import setup_client
from .client import LoginRequired, LoginFailed
from requests.exceptions import RequestException
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWD, CONF_HOST, CONF_VERIFY_SSL, CONF_CACHE_SECONDS, CONF_NAME, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWD): str,
        vol.Optional(CONF_VERIFY_SSL, default=True): bool,
        vol.Optional(CONF_CACHE_SECONDS, default=30): int,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nginx Proxy Manager Access."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        
        errors = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
            try:
                await self.hass.async_add_executor_job(
                    setup_client,
                    user_input[CONF_HOST],
                    user_input[CONF_EMAIL],
                    user_input[CONF_PASSWD],
                    user_input[CONF_VERIFY_SSL],
                    user_input[CONF_CACHE_SECONDS],
                )
            except LoginRequired:
                errors = {"base": "invalid_auth"}
            except LoginFailed:
                errors = {"base": "invalid_auth"}
            except RequestException:
                errors = {"base": "cannot_connect"}
            else:
                return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        schema = self.add_suggested_values_to_schema(USER_DATA_SCHEMA, user_input)
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, config: dict[str, Any]) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        self._async_abort_entries_match({CONF_HOST: config[CONF_HOST]})
        return self.async_create_entry(
            title=config.get(CONF_NAME, DEFAULT_NAME),
            data={
                CONF_HOST: config[CONF_HOST],
                CONF_EMAIL: config[CONF_EMAIL],
                CONF_PASSWD: config[CONF_PASSWD],
                CONF_VERIFY_SSL: config[CONF_PASSWD],
                CONF_CACHE_SECONDS: config[CONF_CACHE_SECONDS],
            },
        )


