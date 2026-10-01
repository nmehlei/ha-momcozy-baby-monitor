"""Button platform for momcozy_baby_monitor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .release_button import MomcozyBabyMonitorReleaseButton
from .retry_button import MomcozyBabyMonitorRetryButton

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import MomcozyBabyMonitorCameraConfig, MomcozyBabyMonitorConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 -- part of the signature Home Assistant calls
    entry: MomcozyBabyMonitorConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up recovery controls for every configured camera."""
    cameras: list[MomcozyBabyMonitorCameraConfig] = list(entry.data["cameras"])
    entities: list[MomcozyBabyMonitorRetryButton | MomcozyBabyMonitorReleaseButton] = []
    for camera in cameras:
        entities.extend(
            (
                MomcozyBabyMonitorRetryButton(
                    entry.runtime_data.coordinator,
                    camera["device_id"],
                    camera["name"],
                ),
                MomcozyBabyMonitorReleaseButton(
                    entry.runtime_data.coordinator,
                    camera["device_id"],
                    camera["name"],
                ),
            )
        )
    async_add_entities(entities)
