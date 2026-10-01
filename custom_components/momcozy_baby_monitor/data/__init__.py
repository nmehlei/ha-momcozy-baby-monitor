"""Custom types for momcozy_baby_monitor."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from .camera_config import MomcozyBabyMonitorCameraConfig
from .camera_state import MomcozyBabyMonitorCameraState
from .config_data import MomcozyBabyMonitorConfigData
from .credentials import MomcozyBabyMonitorCredentials
from .diagnostics_entry import MomcozyBabyMonitorDiagnosticsEntry
from .diagnostics_payload import MomcozyBabyMonitorDiagnosticsPayload
from .options_data import MomcozyBabyMonitorOptionsData
from .runtime import MomcozyBabyMonitorData
from .stream_diagnostics import MomcozyBabyMonitorStreamDiagnostics

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonPrimitive | list[JsonValue] | Mapping[str, JsonValue]
type JsonObject = Mapping[str, JsonValue]

type MomcozyBabyMonitorPayload = dict[str, MomcozyBabyMonitorCameraState]

type MomcozyBabyMonitorConfigEntry = ConfigEntry[MomcozyBabyMonitorData]

__all__ = [
    "JsonObject",
    "JsonPrimitive",
    "JsonValue",
    "MomcozyBabyMonitorCameraConfig",
    "MomcozyBabyMonitorCameraState",
    "MomcozyBabyMonitorConfigData",
    "MomcozyBabyMonitorConfigEntry",
    "MomcozyBabyMonitorCredentials",
    "MomcozyBabyMonitorData",
    "MomcozyBabyMonitorDiagnosticsEntry",
    "MomcozyBabyMonitorDiagnosticsPayload",
    "MomcozyBabyMonitorOptionsData",
    "MomcozyBabyMonitorPayload",
    "MomcozyBabyMonitorStreamDiagnostics",
]
