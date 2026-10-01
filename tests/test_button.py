from __future__ import annotations

from homeassistant.const import ATTR_ENTITY_ID


async def _press(hass, entity_id: str) -> None:
    await hass.services.async_call(
        "button",
        "press",
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )


async def test_retry_button_wakes_the_stream(hass, setup_integration, camera_stream):
    await _press(hass, "button.feeder_retry_connection")

    assert camera_stream.retry_calls == 1
    assert camera_stream.running is True


async def test_release_button_stops_the_stream(hass, setup_integration, camera_stream):
    camera_stream.running = True
    camera_stream.notify()
    await hass.async_block_till_done()

    await _press(hass, "button.feeder_release_session")

    assert camera_stream.running is False
    assert camera_stream.stop_calls == 1
