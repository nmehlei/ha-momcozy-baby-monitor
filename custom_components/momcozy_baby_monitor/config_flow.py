"""Config flow for momcozy_baby_monitor."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.util import slugify

from .api import MomcozyBabyMonitorApiClient
from .const import DOMAIN, LOGGER
from .exceptions import (
    MomcozyBabyMonitorApiClientAuthenticationError,
    MomcozyBabyMonitorApiClientCommunicationError,
    MomcozyBabyMonitorApiClientError,
)
from .options_flow import MomcozyBabyMonitorOptionsFlow

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .data import (
        MomcozyBabyMonitorCameraConfig,
        MomcozyBabyMonitorConfigData,
        MomcozyBabyMonitorConfigEntry,
        MomcozyBabyMonitorCredentials,
    )

MOMCOZY_REGIONS: tuple[str, ...] = ("eu", "us", "cn", "in")


def _credentials_schema(defaults: Mapping[str, str] | None = None) -> vol.Schema:
    """Build the account form, optionally pre-filled from an existing entry."""
    known = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                "email",
                default=known.get("email", vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.EMAIL),
            ),
            vol.Required("password"): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
            ),
            vol.Required(
                "country_code",
                default=known.get("country_code", vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
            ),
            vol.Required(
                "region",
                default=known.get("region", "eu"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(MOMCOZY_REGIONS),
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    translation_key="region",
                ),
            ),
        },
    )


class MomcozyBabyMonitorFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Momcozy Baby Monitor."""

    VERSION = 1

    def __init__(self) -> None:
        """Start with nothing discovered."""
        self._cameras: list[MomcozyBabyMonitorCameraConfig] = []

    @staticmethod
    def _account_unique_id(user_input: MomcozyBabyMonitorCredentials) -> str:
        """Namespace the account identifier to Momcozy."""
        return slugify(f"momcozy_{user_input['email']}")

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: MomcozyBabyMonitorConfigEntry,  # noqa: ARG004
    ) -> MomcozyBabyMonitorOptionsFlow:
        """Return the options flow handler."""
        return MomcozyBabyMonitorOptionsFlow()

    # The narrowed ``MomcozyBabyMonitorCredentials`` parameter is intentional — HA's
    # base class declares ``dict[str, Any] | None`` here, and we trade strict
    # LSP compliance for stronger typing of our own user_input schema.
    async def async_step_user(  # type: ignore[override]
        self,
        user_input: MomcozyBabyMonitorCredentials | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Collect the account, then discover the cameras it can stream."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = await self._async_validate(user_input)
            if not errors:
                await self.async_set_unique_id(self._account_unique_id(user_input))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input["email"],
                    data=self._entry_data(user_input),
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_credentials_schema(
                cast("Mapping[str, str]", user_input) if user_input else None
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: Mapping[str, str],  # noqa: ARG002
    ) -> config_entries.ConfigFlowResult:
        """Trigger reauth when the cloud rejects the stored credentials."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: MomcozyBabyMonitorCredentials | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Prompt for new credentials, keeping the cameras already configured.

        Re-authenticating is not the moment to re-run discovery: it probes the
        IPC config API once per device on the account, and the cameras have not
        changed just because the password did.
        """
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        existing = cast("MomcozyBabyMonitorConfigData", entry.data)

        if user_input is not None:
            errors = await self._async_validate(user_input, discover=False)
            if not errors:
                await self.async_set_unique_id(self._account_unique_id(user_input))
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=dict(user_input),
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=_credentials_schema(cast("Mapping[str, str]", existing)),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: MomcozyBabyMonitorCredentials | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Edit the account and refresh the camera list from it."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()
        existing = cast("MomcozyBabyMonitorConfigData", entry.data)

        if user_input is not None:
            errors = await self._async_validate(user_input)
            if not errors:
                await self.async_set_unique_id(self._account_unique_id(user_input))
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=dict(self._entry_data(user_input)),
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_credentials_schema(cast("Mapping[str, str]", existing)),
            errors=errors,
        )

    def _entry_data(
        self, user_input: MomcozyBabyMonitorCredentials
    ) -> MomcozyBabyMonitorConfigData:
        """Assemble what the entry persists: the account and its cameras."""
        return {
            "email": user_input["email"],
            "password": user_input["password"],
            "country_code": user_input["country_code"],
            "region": user_input["region"],
            "cameras": self._cameras,
        }

    async def _async_validate(
        self, user_input: MomcozyBabyMonitorCredentials, *, discover: bool = True
    ) -> dict[str, str]:
        """Test the account and, when asked, discover its cameras."""
        client = MomcozyBabyMonitorApiClient(
            email=user_input["email"],
            password=user_input["password"],
            country_code=user_input["country_code"],
            region=user_input["region"],
            session=async_create_clientsession(self.hass),
        )
        try:
            await client.async_verify_credentials()
            if discover:
                self._cameras = await client.async_discover_cameras()
        except MomcozyBabyMonitorApiClientAuthenticationError as exception:
            LOGGER.warning("Failed to authenticate: %s", exception)
            return {"base": "auth"}
        except MomcozyBabyMonitorApiClientCommunicationError as exception:
            LOGGER.error("Failed to reach the account service: %s", exception)
            return {"base": "connection"}
        except MomcozyBabyMonitorApiClientError:
            LOGGER.exception("Failed to validate the account")
            return {"base": "unknown"}
        if discover and not self._cameras:
            return {"base": "no_cameras"}
        return {}
