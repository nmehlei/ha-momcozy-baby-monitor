"""Typed shape of what one running stream reports to diagnostics."""

from __future__ import annotations

from typing import TypedDict


class MomcozyBabyMonitorStreamDiagnostics(TypedDict):
    """What a supervised stream reports about itself."""

    running: bool
    streaming: bool
    motion_detected: bool
    viewer_count: int
    last_frame_bytes: int | None
