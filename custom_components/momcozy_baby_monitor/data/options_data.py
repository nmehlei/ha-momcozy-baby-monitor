"""Typed shape of the options writable by the options flow."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class MomcozyBabyMonitorOptionsData(TypedDict, total=False):
    """Shape of the options writable by the options flow."""

    scan_interval: NotRequired[int]
    keep_connected: NotRequired[bool]
    motion_sensitivity: NotRequired[float]
    wake_on_snapshot: NotRequired[bool]
