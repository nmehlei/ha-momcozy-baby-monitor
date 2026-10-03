# Changelog

## 0.1.1 - 2026-10-03

### Fixes

- publish the HACS archive when a GitHub release already exists
- preserve immutable release tags when retrying publication

## 0.1.0 - 2026-10-02

### Features

- sign in with a Momcozy account and discover BM04 cameras automatically
- expose live video, cached snapshots and frame-derived motion
- share the camera's single session with the Momcozy app through on-demand use
- retry immediately after camera or network recovery
- provide retry and release-session controls
- raise a repair issue when the camera needs a power cycle

### Privacy and safety

- redact account credentials and local keys from diagnostics
- prevent dashboard thumbnails from taking an idle camera session by default
- document cloud relay use, credential storage and monitoring limitations
