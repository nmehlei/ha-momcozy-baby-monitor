# Brand assets

Home Assistant 2026.3+ serves this directory directly, so these files are what
every user sees — nothing is submitted to `home-assistant/brands` any more.

The monitor-and-heart mark is original project artwork. It intentionally avoids
the Momcozy and Tuya corporate marks so the community integration is easy to
recognise without implying vendor endorsement. The concept was generated with
OpenAI ImageGen and refined into a native SVG plus deterministic PNG assets.

Run `python scripts/generate_brand_assets.py` from the repository root to
regenerate the PNG files after changing the master design.

| File          | Shape                   | Size     |
| ------------- | ----------------------- | -------- |
| `icon.png`    | square symbol           | 256×256  |
| `icon@2x.png` | square symbol           | 512×512  |
| `icon.svg`    | square vector of `icon` | vector   |
| `dark_icon.png` / `dark_icon@2x.png` | dark-theme symbol | 256×256 / 512×512 |
| `logo.png`    | landscape wordmark      | 512×256  |
| `logo@2x.png` | landscape wordmark      | 1024×512 |
| `dark_logo.png` / `dark_logo@2x.png` | dark-theme wordmark | 512×256 / 1024×512 |

The artwork is distributed under the repository's MIT license.
