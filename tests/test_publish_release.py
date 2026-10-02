from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PUBLISHER = ROOT / "scripts" / "publish_release.py"


def _fake_gh(tmp_path: Path, *, release_exists: bool) -> tuple[Path, Path]:
    log = tmp_path / "gh.log"
    if os.name == "nt":
        executable = tmp_path / "gh.cmd"
        view_exit = 0 if release_exists else 1
        executable.write_text(
            "@echo off\n"
            f'echo %*>>"{log}"\n'
            f'if "%1 %2"=="release view" exit /b {view_exit}\n'
            "exit /b 0\n",
            encoding="utf-8",
        )
    else:
        executable = tmp_path / "gh"
        view_exit = 0 if release_exists else 1
        executable.write_text(
            "#!/bin/sh\n"
            f'printf "%s\\n" "$*" >> "{log}"\n'
            f'[ "$1 $2" = "release view" ] && exit {view_exit}\n'
            "exit 0\n",
            encoding="utf-8",
        )
        executable.chmod(executable.stat().st_mode | stat.S_IEXEC)
    return executable, log


def test_an_existing_release_receives_the_archive(tmp_path: Path):
    _, log = _fake_gh(tmp_path, release_exists=True)
    env = os.environ | {"PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}"}

    result = subprocess.run(
        [sys.executable, PUBLISHER, "v0.1.0", "momcozy_baby_monitor.zip"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert log.read_text(encoding="utf-8").splitlines() == [
        "release view v0.1.0",
        "release upload v0.1.0 momcozy_baby_monitor.zip --clobber",
    ]


def test_a_tag_without_a_release_creates_one(tmp_path: Path):
    _, log = _fake_gh(tmp_path, release_exists=False)
    env = os.environ | {"PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}"}

    result = subprocess.run(
        [sys.executable, PUBLISHER, "v0.2.0", "momcozy_baby_monitor.zip"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert log.read_text(encoding="utf-8").splitlines() == [
        "release view v0.2.0",
        (
            "release create v0.2.0 momcozy_baby_monitor.zip --generate-notes "
            "--verify-tag"
        ),
    ]
