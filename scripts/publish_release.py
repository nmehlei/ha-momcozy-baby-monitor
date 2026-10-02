# ruff: noqa: INP001
"""Create a GitHub release or replace its HACS archive when it already exists."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _gh_command(*arguments: str) -> list[str]:
    """Return a directly executable command for the installed GitHub CLI."""
    executable = shutil.which("gh")
    if executable is None:
        msg = "GitHub CLI executable not found"
        raise FileNotFoundError(msg)
    if os.name == "nt" and Path(executable).suffix.lower() in {".bat", ".cmd"}:
        return [
            os.environ.get("COMSPEC", "cmd.exe"),
            "/d",
            "/c",
            executable,
            *arguments,
        ]
    return [executable, *arguments]


def main(tag: str, archive: str) -> None:
    """Publish *archive* for *tag* without failing when the release exists."""
    release_exists = (
        subprocess.run(  # noqa: S603
            _gh_command("release", "view", tag),
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )

    if release_exists:
        command = _gh_command("release", "upload", tag, archive, "--clobber")
    else:
        command = _gh_command(
            "release",
            "create",
            tag,
            archive,
            "--generate-notes",
            "--verify-tag",
        )

    subprocess.run(command, check=True)  # noqa: S603


if __name__ == "__main__":
    main(*sys.argv[1:])
