"""Runtime data stored on entry.runtime_data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.loader import Integration
    from tuya_ipc_p2p_sdk import CameraStream

    from ..api import MomcozyBabyMonitorApiClient
    from ..coordinator import MomcozyBabyMonitorDataUpdateCoordinator
    from ..stream_server import MomcozyBabyMonitorStreamServer


@dataclass
class MomcozyBabyMonitorData:
    """
    Data stored on entry.runtime_data for Momcozy Baby Monitor.

    ``streams`` holds one supervised stream per configured camera, keyed by
    device id. They live here rather than on the entities because the camera
    and the motion sensor of one device read the same stream, and the stream
    server serves all of them on one loopback port.
    """

    client: MomcozyBabyMonitorApiClient
    coordinator: MomcozyBabyMonitorDataUpdateCoordinator
    integration: Integration
    stream_server: MomcozyBabyMonitorStreamServer
    streams: dict[str, CameraStream] = field(default_factory=dict)
