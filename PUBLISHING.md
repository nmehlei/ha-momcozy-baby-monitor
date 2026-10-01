# Publishing checklist

This repository uses an immutable SDK commit while the upstream Momcozy pull
request is under review. That pin is suitable for development and isolated
testing, but the first stable release remains blocked on a PyPI SDK release.

Before the first release:

1. Obtain an upstream SDK release containing the Momcozy changes, then replace
   the immutable Git requirement in both `manifest.json` and `pyproject.toml`
   with the exact PyPI version.
2. Regenerate `uv.lock` and confirm it resolves the released SDK artifact.
3. Run Linux CI, including the three process tests that use a Unix fake
   encoder.
4. Create the repository, then add its public URL and HACS installation button
   to `README.md`.
5. Tag `v0.1.0`; the release workflow builds and attaches the HACS zip.

Never add the research APK, decompiled output, private credentials or a local
vendored SDK copy to this repository.
