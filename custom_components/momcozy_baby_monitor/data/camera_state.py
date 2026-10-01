"""Typed shape of what a poll knows about one camera."""

from __future__ import annotations

from typing import TypedDict


class MomcozyBabyMonitorCameraState(TypedDict):
    """What the account's device list reports about one configured camera."""

    name: str
    online: bool
    local_key: str
