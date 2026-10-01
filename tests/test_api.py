from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tuya_ipc_p2p_sdk import (
    TuyaDevice,
    TuyaIpcP2pAuthenticationError,
    TuyaIpcP2pConnectionError,
    TuyaIpcP2pError,
    TuyaIpcP2pProtocolError,
)

from custom_components.momcozy_baby_monitor.api import MomcozyBabyMonitorApiClient
from custom_components.momcozy_baby_monitor.exceptions import (
    MomcozyBabyMonitorApiClientAuthenticationError,
    MomcozyBabyMonitorApiClientCommunicationError,
    MomcozyBabyMonitorApiClientError,
)

CAMERA = TuyaDevice(
    "cam-1",
    "Feeder",
    "cwwsq",
    "0123456789abcdef",
    product_id="mzohju3minbjogwz",
)
PLUG = TuyaDevice("plug-1", "Plug", "cz", "fedcba9876543210", online=False)
BM04 = TuyaDevice(
    "bm04-1",
    "BM04",
    "sp",
    "0011223344556677",
    product_id="mzohju3minbjogwz",
)
OTHER_CAMERA = TuyaDevice(
    "other-1",
    "Other camera",
    "sp",
    "8899aabbccddeeff",
    product_id="not-the-bm04",
)


@pytest.fixture
def sdk():
    with patch(
        "custom_components.momcozy_baby_monitor.api.MomcozyIpcP2pClient"
    ) as mock_class:
        instance = mock_class.return_value
        instance.async_login = AsyncMock(return_value=None)
        instance.async_list_devices = AsyncMock(return_value=[CAMERA, PLUG])
        instance.create_camera_stream = MagicMock(return_value="a-stream")
        instance.async_close = AsyncMock(return_value=None)
        yield instance


def _client() -> MomcozyBabyMonitorApiClient:
    return MomcozyBabyMonitorApiClient(
        email="user@example.com",
        password="hunter2",
        country_code="55",
        region="us",
        session=MagicMock(),
    )


async def test_momcozy_discovery_uses_the_product_list_without_probing_streams():
    with patch(
        "custom_components.momcozy_baby_monitor.api.MomcozyIpcP2pClient"
    ) as mock_class:
        sdk = mock_class.return_value
        sdk.async_list_devices = AsyncMock(return_value=[BM04, OTHER_CAMERA])
        sdk.async_discover_cameras = AsyncMock()
        client = MomcozyBabyMonitorApiClient(
            email="user@example.com",
            password="hunter2",
            country_code="DE",
            region="eu",
            session=MagicMock(),
        )

        assert await client.async_discover_cameras() == [
            {
                "device_id": "bm04-1",
                "name": "BM04",
                "local_key": "0011223344556677",
            }
        ]
        sdk.async_list_devices.assert_awaited_once()
        sdk.async_discover_cameras.assert_not_awaited()


async def test_verifying_credentials_logs_in_for_real(sdk):
    await _client().async_verify_credentials()
    sdk.async_login.assert_awaited_once()


async def test_discovery_returns_the_persisted_shape(sdk):
    assert await _client().async_discover_cameras() == [
        {"device_id": "cam-1", "name": "Feeder", "local_key": "0123456789abcdef"}
    ]


async def test_camera_states_keep_only_the_configured_devices(sdk):
    states = await _client().async_camera_states(frozenset({"cam-1"}))
    assert states == {
        "cam-1": {"name": "Feeder", "online": True, "local_key": "0123456789abcdef"}
    }


async def test_camera_states_carry_the_online_flag(sdk):
    states = await _client().async_camera_states(frozenset({"cam-1", "plug-1"}))
    assert states["plug-1"]["online"] is False


async def test_creating_a_stream_passes_the_sensitivity_through(sdk):
    assert _client().create_stream("cam-1", "key", 12) == "a-stream"
    sdk.create_camera_stream.assert_called_once_with(
        device_id="cam-1", local_key="key", motion_sensitivity=12
    )


async def test_closing_releases_the_sdk_client(sdk):
    await _client().async_close()
    sdk.async_close.assert_awaited_once()


@pytest.mark.parametrize(
    ("raised", "expected"),
    [
        (
            TuyaIpcP2pAuthenticationError("no"),
            MomcozyBabyMonitorApiClientAuthenticationError,
        ),
        (
            TuyaIpcP2pConnectionError("down"),
            MomcozyBabyMonitorApiClientCommunicationError,
        ),
        (TuyaIpcP2pProtocolError("garbage"), MomcozyBabyMonitorApiClientError),
        (TuyaIpcP2pError("something"), MomcozyBabyMonitorApiClientError),
    ],
)
async def test_sdk_errors_never_escape_the_boundary(sdk, raised, expected):
    sdk.async_login = AsyncMock(side_effect=raised)
    with pytest.raises(expected):
        await _client().async_verify_credentials()


async def test_an_unrelated_error_is_left_alone(sdk):
    sdk.async_list_devices = AsyncMock(side_effect=ValueError("not ours"))
    with pytest.raises(ValueError, match="not ours"):
        await _client().async_camera_states(frozenset())
