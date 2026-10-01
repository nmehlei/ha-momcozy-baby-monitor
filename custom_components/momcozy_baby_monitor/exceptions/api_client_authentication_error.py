"""Authentication error raised by the API client."""

from __future__ import annotations

from .api_client_error import MomcozyBabyMonitorApiClientError


class MomcozyBabyMonitorApiClientAuthenticationError(
    MomcozyBabyMonitorApiClientError,
):
    """Exception to indicate an authentication error."""
