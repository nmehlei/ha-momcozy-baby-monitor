# Security policy

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose a camera,
account credential, session token, local key or private video. Use GitHub's
private vulnerability-reporting feature for this repository instead.

Include the affected release, the smallest reproducible description and the
impact. Do not include real credentials, tokens, device identifiers, local
keys, packet captures or camera images. Synthetic or redacted material is
enough to begin an investigation.

## Data handling

The integration authenticates directly from Home Assistant to the services
required by Momcozy and its delegated Tuya services. It has no telemetry or
maintainer-operated relay. Account credentials and device keys are stored in Home
Assistant's config entry and are redacted from diagnostics. Video is served
inside the Home Assistant installation and is not sent to the maintainers.

## Scope

This is an unofficial interoperability project. Vulnerabilities in Momcozy,
Tuya, Home Assistant or camera firmware should also be reported to the vendor
that can fix the affected system.
