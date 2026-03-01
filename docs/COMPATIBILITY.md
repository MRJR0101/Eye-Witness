# Compatibility Policy

## Runtime
- Python versions: `3.10+`
- Supported targets: CLI apps, web services, worker processes

## Dependency Policy
- Eye-Witness follows semver for public API.
- Major upgrades may require coordinated upgrades of:
  - `opentelemetry-*`
  - `sentry-sdk`
  - `structlog`

## Public API Stability
The symbols exported from `eye_witness.__init__` are considered the stable API.
Internal modules prefixed with `_` may change without notice.
