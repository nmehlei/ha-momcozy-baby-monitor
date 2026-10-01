"""Momcozy Baby Monitor integration for Home Assistant."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, cast

from homeassistant.components.ffmpeg import get_ffmpeg_manager
from homeassistant.const import CONF_SCAN_INTERVAL, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import MomcozyBabyMonitorApiClient
from .camera_health import MomcozyBabyMonitorCameraHealth
from .const import (
    CONF_MOTION_SENSITIVITY,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
    LOGGER,
)
from .coordinator import MomcozyBabyMonitorDataUpdateCoordinator
from .data import MomcozyBabyMonitorData
from .issues import async_clear_camera_issues
from .options_flow import DEFAULT_MOTION_SENSITIVITY
from .stream_server import MomcozyBabyMonitorStreamServer

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceEntry

    from .data import MomcozyBabyMonitorConfigData, MomcozyBabyMonitorConfigEntry

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.BUTTON, Platform.CAMERA]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MomcozyBabyMonitorConfigEntry,
) -> bool:
    """Set up Momcozy Baby Monitor from a config entry."""
    config = cast("MomcozyBabyMonitorConfigData", entry.data)
    scan_interval_seconds: int = int(
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS),
    )
    motion_sensitivity = float(
        entry.options.get(CONF_MOTION_SENSITIVITY, DEFAULT_MOTION_SENSITIVITY),
    )
    device_ids = frozenset(camera["device_id"] for camera in config["cameras"])

    client = MomcozyBabyMonitorApiClient(
        email=config["email"],
        password=config["password"],
        country_code=config["country_code"],
        region=config["region"],
        session=async_get_clientsession(hass),
    )
    coordinator = MomcozyBabyMonitorDataUpdateCoordinator(
        hass=hass,
        scan_interval=timedelta(seconds=scan_interval_seconds),
        device_ids=device_ids,
        config_entry=entry,
    )
    streams = {
        camera["device_id"]: client.create_stream(
            device_id=camera["device_id"],
            local_key=camera["local_key"],
            motion_sensitivity=motion_sensitivity,
        )
        for camera in config["cameras"]
    }
    stream_server = MomcozyBabyMonitorStreamServer(
        hass, streams, get_ffmpeg_manager(hass).binary
    )
    entry.runtime_data = MomcozyBabyMonitorData(
        client=client,
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
        stream_server=stream_server,
        streams=streams,
    )

    await coordinator.async_config_entry_first_refresh()

    # A camera that has stopped answering offers comes back only when someone
    # power cycles it, so it is worth saying so where the user looks.
    for camera in config["cameras"]:
        health = MomcozyBabyMonitorCameraHealth(
            hass, entry, streams[camera["device_id"]], camera["name"]
        )
        entry.async_on_unload(health.async_watch())

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: MomcozyBabyMonitorConfigEntry,
) -> bool:
    """
    Handle removal of an entry.

    The streams are stopped whether or not the platforms unload cleanly: each
    one holds a relay connection and a broker session, and a camera that is
    never released refuses the next offer until its own timer fires.
    """
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    async_clear_camera_issues(hass, entry, entry.runtime_data.streams)
    await entry.runtime_data.stream_server.async_stop()
    await asyncio.gather(
        *(stream.async_close() for stream in entry.runtime_data.streams.values())
    )
    await entry.runtime_data.client.async_close()
    return unloaded


async def async_reload_entry(
    hass: HomeAssistant,
    entry: MomcozyBabyMonitorConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant,  # noqa: ARG001 -- part of the signature Home Assistant calls
    entry: MomcozyBabyMonitorConfigEntry,
    device_entry: DeviceEntry,
) -> bool:
    """
    Allow deleting cameras this entry no longer configures.

    Home Assistant hides the "delete device" button unless the integration
    implements this hook, so without it a camera removed from the account stays
    in the registry with all of its entities unavailable, and the only way out
    is deleting the whole config entry.

    A camera the entry still lists is refused — setup would recreate it on the
    next reload anyway. Rediscovering the account through the flow's
    reconfigure step is what removes one from the list.
    """
    config = cast("MomcozyBabyMonitorConfigData", entry.data)
    configured = {(DOMAIN, camera["device_id"]) for camera in config["cameras"]}
    if device_entry.identifiers & configured:
        LOGGER.debug("Refusing to remove a camera the entry still configures")
        return False
    return True
