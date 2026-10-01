"""Communication error raised by the API client."""

from __future__ import annotations

from .api_client_error import MomcozyBabyMonitorApiClientError


class MomcozyBabyMonitorApiClientCommunicationError(
    MomcozyBabyMonitorApiClientError,
):
    """Exception to indicate a communication error."""
