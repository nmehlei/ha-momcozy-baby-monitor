"""Typed top-level shape returned by async_get_config_entry_diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .camera_state import MomcozyBabyMonitorCameraState
    from .diagnostics_entry import MomcozyBabyMonitorDiagnosticsEntry
    from .stream_diagnostics import MomcozyBabyMonitorStreamDiagnostics


class MomcozyBabyMonitorDiagnosticsPayload(TypedDict):
    """Top-level shape returned by async_get_config_entry_diagnostics."""

    entry: MomcozyBabyMonitorDiagnosticsEntry
    coordinator_data: dict[str, MomcozyBabyMonitorCameraState] | None
    streams: dict[str, MomcozyBabyMonitorStreamDiagnostics]
