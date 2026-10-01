# Momcozy Baby Monitor for Home Assistant

An unofficial Home Assistant integration for the **Momcozy BM04** baby
monitor. Sign in with the same Momcozy account used by the mobile app and the
integration discovers the camera automatically—no ADB, APK, device reset,
local-key extraction or Smart Life account is required.

> **Unofficial.** This project is not affiliated with, endorsed by or supported
> by Momcozy or Tuya. Momcozy and BM04 are trademarks of their respective
> owners and are used only to identify compatible hardware.
>
> This integration is not a medical or safety device and is not a substitute
> for direct supervision. Do not make it the only way a child is monitored.

## What it provides

Each BM04 becomes one Home Assistant device with:

| Entity | Purpose |
|---|---|
| Camera | Live video and cached JPEG snapshots |
| Motion sensor | Motion estimated from frames already received |
| Retry connection | Immediately retries after power or network returns |
| Release session | Gives the camera's single video session back to the app |

## Installation

This repository is not published yet. Once released, install it through HACS
as a custom integration repository, restart Home Assistant, then add
**Momcozy Baby Monitor** under **Settings → Devices & services**.

## Configuration

The setup flow asks for:

- Momcozy account email
- Momcozy account password
- two-letter account country code, such as `DE`, `BR` or `US`
- Tuya service region; Europe is the default

The country and region are needed because Momcozy delegates the camera session
to Tuya's regional infrastructure. Device identifiers and local keys are
discovered automatically and never have to be copied from the app.

Home Assistant stores the password in config-entry storage so the integration
can reconnect after a restart. It is never logged and is redacted, together
with account data and local keys, from diagnostics.

## Sharing the camera with the Momcozy app

The BM04 serves one video client at a time. While Home Assistant holds a
session, the Momcozy app cannot show live video, and vice versa.

**Keep connected** is off by default. Home Assistant connects when live video
is requested and releases the session one minute after the last viewer leaves.
Dashboard thumbnail requests use the last cached frame and do not wake an idle
camera unless **Wake for snapshots** is enabled.

## Reliability

- A supervised stream reconnects after transport failures and stalls.
- A camera returning online or rotating its local key interrupts the retry
  delay and triggers an immediate attempt.
- Repeated “busy” responses slow the retry rate instead of hammering a camera
  that needs a power cycle.
- Home Assistant raises a repair issue if the camera reaches that state and
  removes it automatically after video recovers.
- **Retry connection** and **Release session** provide manual recovery without
  restarting Home Assistant.

## How it works

Momcozy authentication returns delegated Tuya credentials. The companion
[`tuya-ipc-p2p-sdk`](https://github.com/roquerodrigo/tuya-ipc-p2p-sdk)
performs Tuya gateway login, MQTT signaling and encrypted relay transport, then
hands JPEG frames to this integration. Home Assistant previews use those JPEGs
directly; integrations requiring H.264 receive a loopback MPEG-TS stream
encoded by Home Assistant's ffmpeg installation.

Video therefore uses the vendor's cloud-coordinated relay and is not fully
local.

## Development

```bash
scripts/setup
scripts/lint
```

The lint command runs Ruff, strict mypy and the complete pytest suite with a
90% coverage requirement. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the
workflow and [`NOTICE`](NOTICE) for upstream attribution.

Security reports should follow [`SECURITY.md`](SECURITY.md).

## License

MIT. See [`LICENSE`](LICENSE).

