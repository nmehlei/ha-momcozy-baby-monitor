"""Button that asks a camera stream to retry immediately."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory

from .entity import MomcozyBabyMonitorEntity


class MomcozyBabyMonitorRetryButton(MomcozyBabyMonitorEntity, ButtonEntity):
    """Wake a camera stream from its reconnect cooldown."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "retry"

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from the Tuya device id."""
        return f"{self._device_id}_retry"

    async def async_press(self) -> None:
        """Retry the camera immediately."""
        await self.camera_stream.async_retry_now()
