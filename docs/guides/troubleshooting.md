# Troubleshooting Guide

- No traces: ensure `otel_exporter` is not `"none"`.
- No metrics: enable `metrics_enabled=True`.
- Duplicate logs: set `log_clear_root_handlers=False` in host-managed apps.
