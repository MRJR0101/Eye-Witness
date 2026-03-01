# Runbooks

## Emergency disable tracing
Set `EW_OTEL_EXPORTER=none`.

## Emergency disable metrics
Set `EW_METRICS_ENABLED=false`.

## Reduce telemetry volume
Lower `EW_OTEL_SAMPLE_RATE` and adjust `EW_OTEL_SPAN_NAME_SAMPLE_RATES`.
