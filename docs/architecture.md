# Architecture

Eye-Witness composes:
- Structlog for structured logs
- Sentry SDK for error tracking
- OpenTelemetry for tracing and metrics

Lifecycle:
1. `init()` configures logging
2. `init()` configures Sentry
3. `init()` configures tracing
4. `init()` configures metrics
5. `shutdown()` flushes and tears down providers
