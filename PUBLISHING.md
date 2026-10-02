# Publishing checklist

This repository uses an immutable SDK commit from the maintainer's public fork
while the upstream Momcozy pull request is under review. Home Assistant
supports public Git requirements, and the exact commit pin makes the release
reproducible without following a moving branch.

Release process:

1. Confirm the immutable Git requirement in `manifest.json` and
   `pyproject.toml` references the SDK commit tested by CI.
2. Regenerate `uv.lock` and confirm it resolves that SDK revision.
3. Run Linux CI, including the process tests that use a Unix fake
   encoder.
4. Tag the release; the release workflow builds and attaches the HACS zip.

When the upstream project publishes a release containing the Momcozy changes,
replace the Git requirement with an exact PyPI version in both dependency
files, regenerate `uv.lock`, and run the full verification suite before the
next integration release.

Never add the research APK, decompiled output, private credentials or a local
vendored SDK copy to this repository.
