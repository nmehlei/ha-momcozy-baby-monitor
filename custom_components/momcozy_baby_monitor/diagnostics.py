"""Diagnostics support for momcozy_baby_monitor."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.components.diagnostics import async_redact_data

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import HomeAssistant

    from .data import (
        MomcozyBabyMonitorCameraState,
        MomcozyBabyMonitorConfigEntry,
        MomcozyBabyMonitorDiagnosticsEntry,
        MomcozyBabyMonitorDiagnosticsPayload,
        MomcozyBabyMonitorStreamDiagnostics,
    )

# The local key is what encrypts the signaling and derives the channel-0
# credential, so it belongs in a dump no more than the password does.
TO_REDACT: frozenset[str] = frozenset(
    {"email", "password", "country_code", "local_key"}
)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001 -- part of the signature Home Assistant calls
    entry: MomcozyBabyMonitorConfigEntry,
) -> MomcozyBabyMonitorDiagnosticsPayload:
    """Return diagnostics for a config entry."""
    redacted_data = cast(
        "Mapping[str, str]",
        async_redact_data(dict(entry.data), set(TO_REDACT)),
    )
    redacted_options = cast(
        "Mapping[str, str | int]",
        async_redact_data(dict(entry.options), set(TO_REDACT)),
    )
    diag_entry: MomcozyBabyMonitorDiagnosticsEntry = {
        "title": entry.title,
        "version": entry.version,
        "domain": entry.domain,
        "data": redacted_data,
        "options": redacted_options,
    }
    streams: dict[str, MomcozyBabyMonitorStreamDiagnostics] = {
        device_id: {
            "running": stream.running,
            "streaming": stream.streaming,
            "motion_detected": stream.motion_detected,
            "viewer_count": stream.viewer_count,
            "last_frame_bytes": (
                len(stream.last_frame) if stream.last_frame is not None else None
            ),
        }
        for device_id, stream in entry.runtime_data.streams.items()
    }
    coordinator_data: dict[str, MomcozyBabyMonitorCameraState] | None = (
        entry.runtime_data.coordinator.data
    )
    return {
        "entry": diag_entry,
        "coordinator_data": (
            cast(
                "dict[str, MomcozyBabyMonitorCameraState]",
                async_redact_data(coordinator_data, set(TO_REDACT)),
            )
            if coordinator_data is not None
            else None
        ),
        "streams": streams,
    }
