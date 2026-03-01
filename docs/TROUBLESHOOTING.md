# Troubleshooting

## No traces visible
- Ensure `otel_enabled=True`.
- Set `otel_exporter` to `console` for local checks.
- Confirm endpoint when using OTLP exporters.

## No metrics visible
- Ensure `metrics_enabled=True`.
- Set `metrics_exporter=console` to verify local output.
- For OTLP metrics, set `metrics_endpoint` correctly.

## Logs missing trace IDs
- Ensure spans are active (`trace_span(...)`).
- Confirm logging is initialized through `init()`.

## Sensitive values in logs
- Configure `log_redact_keys`.
- Confirm fields are emitted as key/value pairs, not raw strings.
