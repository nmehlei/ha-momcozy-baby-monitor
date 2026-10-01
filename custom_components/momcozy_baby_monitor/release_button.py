"""Button that releases a camera session for another client."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory

from .entity import MomcozyBabyMonitorEntity


class MomcozyBabyMonitorReleaseButton(MomcozyBabyMonitorEntity, ButtonEntity):
    """Release the camera so the vendor app can use its single session."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "release"

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from the Tuya device id."""
        return f"{self._device_id}_release"

    @property
    def available(self) -> bool:
        """Expose the action only while a supervisor owns the camera."""
        return super().available and self.camera_stream.running

    async def async_added_to_hass(self) -> None:
        """Subscribe to stream state changes."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.camera_stream.add_state_listener(self._async_stream_state_changed)
        )

    def _async_stream_state_changed(self) -> None:
        """Update availability when the supervised stream changes state."""
        self.async_write_ha_state()

    async def async_press(self) -> None:
        """Stop the supervised stream and release its session."""
        await self.camera_stream.async_stop()
