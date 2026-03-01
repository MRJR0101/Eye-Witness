# Changelog

## Unreleased

### Added
- Metrics pipeline and helpers (`get_meter`, `metric_counter`, `metric_histogram`).
- Redaction controls for sensitive log fields.
- Span-name sampling override support.
- FastAPI/Flask/Celery/Django integration helpers.
- CI and publish workflows.
- Ruff and mypy quality gates.
- Benchmark and release-check scripts.
- Troubleshooting, compatibility, and deprecation docs.

### Changed
- `init()` supports forced reinitialization with `force=True`.
- Shutdown is idempotent and centralized.
- `otel_exporter="none"` now truly suppresses exports.
