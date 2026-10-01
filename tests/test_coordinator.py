from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

from custom_components.momcozy_baby_monitor.coordinator import FAILURE_GRACE_PERIOD
from custom_components.momcozy_baby_monitor.exceptions import (
    MomcozyBabyMonitorApiClientAuthenticationError,
    MomcozyBabyMonitorApiClientCommunicationError,
)
from tests.doubles import DEVICE_ID


async def test_the_first_refresh_publishes_the_camera_states(hass, setup_integration):
    coordinator = setup_integration.runtime_data.coordinator
    assert coordinator.data[DEVICE_ID]["name"] == "Feeder"


async def test_an_authentication_failure_asks_for_reauth(
    hass, setup_integration, mock_api_client
):
    mock_api_client.async_camera_states = AsyncMock(
        side_effect=MomcozyBabyMonitorApiClientAuthenticationError("expired")
    )
    coordinator = setup_integration.runtime_data.coordinator
    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


async def test_a_short_outage_serves_the_last_known_values(
    hass, setup_integration, mock_api_client, camera_states
):
    coordinator = setup_integration.runtime_data.coordinator
    mock_api_client.async_camera_states = AsyncMock(
        side_effect=MomcozyBabyMonitorApiClientCommunicationError("blip")
    )
    assert await coordinator._async_update_data() == camera_states


async def test_an_outage_past_the_grace_period_fails_the_refresh(
    hass, setup_integration, mock_api_client
):
    coordinator = setup_integration.runtime_data.coordinator
    mock_api_client.async_camera_states = AsyncMock(
        side_effect=MomcozyBabyMonitorApiClientCommunicationError("still down")
    )
    await coordinator._async_update_data()
    coordinator._first_failure_at = (
        dt_util.utcnow() - FAILURE_GRACE_PERIOD - timedelta(seconds=1)
    )
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_a_recovery_clears_the_failure_window(
    hass, setup_integration, mock_api_client, camera_states
):
    coordinator = setup_integration.runtime_data.coordinator
    mock_api_client.async_camera_states = AsyncMock(
        side_effect=MomcozyBabyMonitorApiClientCommunicationError("blip")
    )
    await coordinator._async_update_data()
    assert coordinator._first_failure_at is not None

    mock_api_client.async_camera_states = AsyncMock(return_value=camera_states)
    await coordinator._async_update_data()
    assert coordinator._first_failure_at is None


async def test_a_rotated_local_key_reaches_the_stream(
    hass, setup_integration, mock_api_client, camera_stream
):
    coordinator = setup_integration.runtime_data.coordinator
    mock_api_client.async_camera_states = AsyncMock(
        return_value={
            DEVICE_ID: {"name": "Feeder", "online": True, "local_key": "rotated-key"}
        }
    )
    await coordinator._async_update_data()
    assert camera_stream.local_key == "rotated-key"


async def test_an_online_transition_wakes_a_running_stream(
    hass, setup_integration, mock_api_client, camera_stream
):
    coordinator = setup_integration.runtime_data.coordinator
    camera_stream.running = True
    mock_api_client.async_camera_states = AsyncMock(
        return_value={
            DEVICE_ID: {
                "name": "Feeder",
                "online": False,
                "local_key": camera_stream.local_key,
            }
        }
    )
    await coordinator._async_update_data()
    mock_api_client.async_camera_states = AsyncMock(
        return_value={
            DEVICE_ID: {
                "name": "Feeder",
                "online": True,
                "local_key": camera_stream.local_key,
            }
        }
    )

    await coordinator._async_update_data()

    assert camera_stream.retry_calls == 1


async def test_an_online_transition_does_not_start_an_idle_stream(
    hass, setup_integration, mock_api_client, camera_stream
):
    coordinator = setup_integration.runtime_data.coordinator
    mock_api_client.async_camera_states = AsyncMock(
        return_value={
            DEVICE_ID: {
                "name": "Feeder",
                "online": False,
                "local_key": camera_stream.local_key,
            }
        }
    )
    await coordinator._async_update_data()
    mock_api_client.async_camera_states = AsyncMock(
        return_value={
            DEVICE_ID: {
                "name": "Feeder",
                "online": True,
                "local_key": camera_stream.local_key,
            }
        }
    )

    await coordinator._async_update_data()

    assert camera_stream.retry_calls == 0


async def test_a_camera_missing_from_the_poll_leaves_the_stream_alone(
    hass, setup_integration, mock_api_client, camera_stream
):
    coordinator = setup_integration.runtime_data.coordinator
    mock_api_client.async_camera_states = AsyncMock(return_value={})
    await coordinator._async_update_data()
    assert camera_stream.local_key == "0123456789abcdef"
