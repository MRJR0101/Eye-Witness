# Local Observability Stack

## Start
Run from repo root:

```powershell
docker compose -f docker-compose.observability.yml up -d
```

## Configure Eye-Witness
Use OTLP exporters:

```python
from eye_witness import init

init(
    service_name="my-app",
    otel_exporter="otlp-http",
    otel_endpoint="http://localhost:4318/v1/traces",
    metrics_enabled=True,
    metrics_exporter="otlp-http",
    metrics_endpoint="http://localhost:4318/v1/metrics",
)
```

## View Data
- Jaeger UI: `http://localhost:16686`

## Stop

```powershell
docker compose -f docker-compose.observability.yml down
```
