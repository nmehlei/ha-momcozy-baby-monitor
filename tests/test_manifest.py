from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).parent.parent
MANIFEST = ROOT / "custom_components" / "momcozy_baby_monitor" / "manifest.json"
SDK_PACKAGE = "tuya-ipc-p2p-sdk"
SDK_COMMIT = "ad6a1cb48ad776988a7aff7efc837da8d5b70cd7"
SDK_REQUIREMENT = (
    "tuya-ipc-p2p-sdk @ "
    "git+https://github.com/nmehlei/tuya-ipc-p2p-sdk.git@"
    f"{SDK_COMMIT}"
)


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_the_sdk_version_home_assistant_installs_is_the_tested_one():
    """The manifest pin and the dev-group pin must not drift apart."""
    requirement = next(
        item for item in _manifest()["requirements"] if item.startswith(SDK_PACKAGE)
    )
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert requirement in pyproject["dependency-groups"]["dev"]


def test_the_sdk_is_pinned_exactly():
    requirement = next(
        item for item in _manifest()["requirements"] if item.startswith(SDK_PACKAGE)
    )
    assert requirement == SDK_REQUIREMENT


def test_the_manifest_has_publishable_repository_metadata():
    manifest = _manifest()
    assert manifest["codeowners"] == ["@nmehlei"]
    assert manifest["documentation"] == (
        "https://github.com/nmehlei/ha-momcozy-baby-monitor"
    )
    assert manifest["issue_tracker"] == (
        "https://github.com/nmehlei/ha-momcozy-baby-monitor/issues"
    )
    assert "YOUR_GITHUB_USERNAME" not in MANIFEST.read_text(encoding="utf-8")


def test_the_manifest_declares_what_hacs_and_hassfest_require():
    manifest = _manifest()
    for key in (
        "domain",
        "name",
        "version",
        "documentation",
        "issue_tracker",
        "codeowners",
        "integration_type",
        "iot_class",
    ):
        assert manifest[key], key
    assert manifest["domain"] == "momcozy_baby_monitor"
    assert manifest["config_flow"] is True
    assert "camera" in manifest["dependencies"]


def test_the_hacs_minimum_matches_the_tested_home_assistant():
    hacs = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pinned = next(
        item
        for item in pyproject["dependency-groups"]["dev"]
        if item.startswith("homeassistant==")
    )
    assert hacs["homeassistant"] == pinned.split("==", 1)[1]
