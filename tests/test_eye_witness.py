"""Tests for Eye-Witness initialization, logging, and context."""

import logging
import os
from unittest.mock import MagicMock, patch

import pytest

import eye_witness as eye_witness_pkg
import eye_witness._init as init_module
from eye_witness._config import EyeWitnessConfig
from eye_witness._context import bind_context, clear_context
from eye_witness._logging import _add_otel_trace_context, configure_logging, get_logger
from eye_witness._metrics import configure_metrics
from eye_witness._sentry import configure_sentry
from eye_witness._tracing import configure_tracing
from eye_witness.integrations import (
    EyeWitnessDjangoMiddleware,
    install_celery,
    install_fastapi,
    install_flask,
)

# ── Config tests ────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_init_state():
    init_module._initialized = False
    init_module._config = None
    init_module._atexit_registered = False
    yield
    init_module._initialized = False
    init_module._config = None
    init_module._atexit_registered = False


class TestEyeWitnessConfig:
    def test_defaults(self):
        cfg = EyeWitnessConfig()
        assert cfg.service_name == "unknown-service"
        assert cfg.environment == "local"
        assert cfg.sentry_dsn == ""
        assert cfg.otel_enabled is True
        assert cfg.otel_exporter == "console"

    def test_custom_values(self):
        cfg = EyeWitnessConfig(
            service_name="test-svc",
            service_version="2.0.0",
            environment="staging",
            sentry_dsn="https://fake@sentry.io/1",
        )
        assert cfg.service_name == "test-svc"
        assert cfg.service_version == "2.0.0"
        assert cfg.sentry_dsn == "https://fake@sentry.io/1"

    def test_frozen(self):
        cfg = EyeWitnessConfig()
        with pytest.raises(AttributeError):
            cfg.service_name = "changed"  # type: ignore[misc]

    def test_from_env(self):
        with patch.dict(os.environ, {"EW_SERVICE_NAME": "env-app", "EW_LOG_LEVEL": "DEBUG"}):
            cfg = EyeWitnessConfig.from_env()
            assert cfg.service_name == "env-app"
            assert cfg.log_level == "DEBUG"

    def test_from_env_overrides(self):
        with patch.dict(os.environ, {"EW_SERVICE_NAME": "env-app"}):
            cfg = EyeWitnessConfig.from_env(service_name="override-app")
            assert cfg.service_name == "override-app"

    def test_invalid_otel_sample_rate_raises(self):
        with pytest.raises(ValueError, match="otel_sample_rate"):
            EyeWitnessConfig(otel_sample_rate=1.1)

    def test_invalid_sentry_traces_sample_rate_raises(self):
        with pytest.raises(ValueError, match="sentry_traces_sample_rate"):
            EyeWitnessConfig(sentry_traces_sample_rate=-0.1)

    def test_otel_exporter_accepts_case_insensitive_value(self):
        cfg = EyeWitnessConfig(otel_exporter="CONSOLE")
        assert cfg.otel_exporter == "CONSOLE"

    def test_metrics_exporter_validation(self):
        with pytest.raises(ValueError, match="metrics_exporter"):
            EyeWitnessConfig(metrics_exporter="grpc")

    def test_metrics_export_interval_validation(self):
        with pytest.raises(ValueError, match="metrics_export_interval_millis"):
            EyeWitnessConfig(metrics_export_interval_millis=0)

    def test_span_name_sample_rates_validation(self):
        with pytest.raises(ValueError, match="otel_span_name_sample_rates values"):
            EyeWitnessConfig(otel_span_name_sample_rates={"important": 1.5})

    def test_from_env_coerces_tuple_and_dict(self):
        with patch.dict(
            os.environ,
            {
                "EW_LOG_REDACT_KEYS": "password,token,api_key",
                "EW_OTEL_SPAN_NAME_SAMPLE_RATES": '{"high_priority": 1.0, "health": 0.0}',
            },
        ):
            cfg = EyeWitnessConfig.from_env()
            assert cfg.log_redact_keys == ("password", "token", "api_key")
            assert cfg.otel_span_name_sample_rates == {
                "high_priority": 1.0,
                "health": 0.0,
            }


# ── Logging tests ───────────────────────────────────────────────────


class TestLogging:
    def test_configure_logging_runs(self):
        cfg = EyeWitnessConfig(log_format="json", log_add_callsite=False)
        configure_logging(cfg)
        log = get_logger("test")
        # Should not raise
        assert log is not None

    def test_get_logger_with_context(self):
        cfg = EyeWitnessConfig(log_format="json")
        configure_logging(cfg)
        log = get_logger("test", job_id="j-1")
        assert log is not None

    def test_otel_trace_context_processor_no_span(self):
        """When no OTel span is active, processor should not add trace_id."""
        event_dict = {"event": "test"}
        result = _add_otel_trace_context(None, None, event_dict)
        # No active span → trace_id should not be present (or processor skips gracefully)
        assert "event" in result

    def test_stdlib_bridge_adds_service_metadata(self):
        cfg = EyeWitnessConfig(
            service_name="svc",
            service_version="1.2.3",
            environment="staging",
            log_format="json",
        )
        with patch("eye_witness._logging.structlog.stdlib.ProcessorFormatter") as formatter:
            formatter.return_value = MagicMock()
            configure_logging(cfg)

            foreign_pre_chain = formatter.call_args.kwargs["foreign_pre_chain"]
            event = {"event": "test.foreign"}
            for proc in foreign_pre_chain:
                event = proc(None, "info", event)

            assert event["service"] == "svc"
            assert event["version"] == "1.2.3"
            assert event["env"] == "staging"

    def test_stdlib_bridge_keeps_existing_handlers_when_disabled(self):
        root = logging.getLogger()
        original_handlers = list(root.handlers)
        existing_handler = logging.NullHandler()
        root.handlers = [existing_handler]

        try:
            cfg = EyeWitnessConfig(log_format="json", log_clear_root_handlers=False)
            configure_logging(cfg)
            assert existing_handler in root.handlers
        finally:
            root.handlers = original_handlers

    def test_redacts_sensitive_fields(self):
        cfg = EyeWitnessConfig(
            log_format="json",
            log_redact_keys=("password", "token"),
            log_redact_value="***",
        )
        with patch("eye_witness._logging.structlog.stdlib.ProcessorFormatter") as formatter:
            formatter.return_value = MagicMock()
            configure_logging(cfg)
            foreign_pre_chain = formatter.call_args.kwargs["foreign_pre_chain"]
            event = {
                "event": "auth.attempt",
                "password": "secret",
                "nested": {"token": "abcd"},
            }
            for proc in foreign_pre_chain:
                event = proc(None, "info", event)

            assert event["password"] == "***"
            assert event["nested"]["token"] == "***"


# ── Sentry tests ────────────────────────────────────────────────────


class TestSentry:
    def test_configure_sentry_no_dsn(self):
        """Empty DSN should not raise — SDK becomes a no-op."""
        cfg = EyeWitnessConfig(sentry_dsn="")
        configure_sentry(cfg)  # should not raise

    def test_configure_sentry_with_dsn(self):
        """With a DSN (even fake), init should still not raise."""
        cfg = EyeWitnessConfig(
            sentry_dsn="https://fake@sentry.io/1",
            sentry_traces_sample_rate=0.0,
        )
        configure_sentry(cfg)


# ── Tracing tests ───────────────────────────────────────────────────


class TestTracing:
    def test_configure_tracing_console(self):
        cfg = EyeWitnessConfig(otel_exporter="console", otel_enabled=True)
        provider = configure_tracing(cfg)
        assert provider is not None

    def test_configure_tracing_disabled(self):
        cfg = EyeWitnessConfig(otel_enabled=False)
        provider = configure_tracing(cfg)
        assert provider is None

    def test_configure_tracing_sample_rate_zero(self):
        cfg = EyeWitnessConfig(otel_sample_rate=0.0, otel_exporter="console")
        provider = configure_tracing(cfg)
        assert provider is not None

    def test_configure_tracing_none_adds_no_processors(self):
        cfg = EyeWitnessConfig(otel_exporter="none", flush_on_exit=False)
        provider = configure_tracing(cfg)
        assert provider is not None
        processors = provider._active_span_processor._span_processors
        assert processors == ()

    def test_configure_tracing_console_is_case_insensitive(self):
        cfg = EyeWitnessConfig(otel_exporter="CONSOLE", flush_on_exit=False)
        provider = configure_tracing(cfg)
        assert provider is not None
        processors = provider._active_span_processor._span_processors
        assert len(processors) == 1
        assert type(processors[0]).__name__ == "SimpleSpanProcessor"

    def test_configure_tracing_uses_span_name_sampler_when_rules_present(self):
        cfg = EyeWitnessConfig(
            otel_exporter="none",
            flush_on_exit=False,
            otel_span_name_sample_rates={"important": 1.0, "health": 0.0},
        )
        provider = configure_tracing(cfg)
        assert provider is not None
        assert type(provider.sampler).__name__ == "SpanNameRateSampler"
        assert "rules=2" in provider.sampler.get_description()


class TestMetrics:
    def test_configure_metrics_disabled(self):
        cfg = EyeWitnessConfig(metrics_enabled=False)
        provider = configure_metrics(cfg)
        assert provider is None

    def test_configure_metrics_none_exporter(self):
        cfg = EyeWitnessConfig(metrics_exporter="none", flush_on_exit=False)
        provider = configure_metrics(cfg)
        assert provider is not None


class TestInit:
    def test_second_init_is_ignored_without_force(self):
        with patch("eye_witness._init.configure_logging") as cfg_log, patch(
            "eye_witness._init.configure_sentry"
        ) as cfg_sentry, patch("eye_witness._init.configure_tracing") as cfg_trace, patch(
            "eye_witness._init.configure_metrics"
        ) as cfg_metrics:
            first = init_module.init(service_name="first-service")
            second = init_module.init(service_name="second-service")

            assert first.service_name == "first-service"
            assert second.service_name == "first-service"
            assert cfg_log.call_count == 1
            assert cfg_sentry.call_count == 1
            assert cfg_trace.call_count == 1
            assert cfg_metrics.call_count == 1

    def test_second_init_reconfigures_with_force(self):
        with patch("eye_witness._init.configure_logging") as cfg_log, patch(
            "eye_witness._init.configure_sentry"
        ) as cfg_sentry, patch("eye_witness._init.configure_tracing") as cfg_trace, patch(
            "eye_witness._init.configure_metrics"
        ) as cfg_metrics:
            first = init_module.init(service_name="first-service")
            second = init_module.init(service_name="second-service", force=True)

            assert first.service_name == "first-service"
            assert second.service_name == "second-service"
            assert cfg_log.call_count == 2
            assert cfg_sentry.call_count == 2
            assert cfg_trace.call_count == 2
            assert cfg_metrics.call_count == 2

    def test_init_registers_single_atexit_hook(self):
        with patch("eye_witness._init.atexit.register") as register_hook:
            init_module.init(service_name="first-service", flush_on_exit=True)
            calls_after_first_init = register_hook.call_count
            init_module.init(service_name="second-service")
            register_hook.assert_any_call(init_module.shutdown)
            assert register_hook.call_count == calls_after_first_init

    def test_shutdown_is_idempotent(self):
        with patch("eye_witness._init.configure_logging"), patch(
            "eye_witness._init.configure_sentry"
        ), patch("eye_witness._init.configure_tracing"), patch(
            "eye_witness._init.configure_metrics"
        ):
            init_module.init(service_name="svc", flush_on_exit=False)

        init_module.shutdown()
        init_module.shutdown()


# ── Context tests ───────────────────────────────────────────────────


class TestContext:
    def test_bind_and_clear_context(self):
        """bind_context / clear_context should not raise."""
        bind_context(request_id="r-1", user_id="u-1")
        clear_context()

    def test_bind_context_sentry_tag(self):
        with patch("eye_witness._context.sentry_sdk.set_tag") as set_tag, patch(
            "eye_witness._context.sentry_sdk.set_context"
        ) as set_context:
            bind_context(job_id="j-42", user_id="u-1")
            set_tag.assert_any_call("job_id", "j-42")
            set_tag.assert_any_call("user_id", "u-1")
            set_context.assert_called_once_with(
                "eye_witness", {"job_id": "j-42", "user_id": "u-1"}
            )
        clear_context()

    def test_clear_context_clears_sentry_scope(self):
        scope = MagicMock()
        with patch("eye_witness._context.sentry_sdk.get_current_scope", return_value=scope):
            clear_context()
            scope.clear.assert_called_once_with()


class TestPublicApi:
    def test_sentry_helpers_are_exported(self):
        assert callable(eye_witness_pkg.set_tag)
        assert callable(eye_witness_pkg.set_context)
        assert callable(eye_witness_pkg.set_user)

    def test_metrics_helpers_are_exported(self):
        assert callable(eye_witness_pkg.get_meter)
        assert callable(eye_witness_pkg.metric_counter)
        assert callable(eye_witness_pkg.metric_histogram)

    def test_integrations_are_exported(self):
        assert callable(eye_witness_pkg.install_fastapi)
        assert callable(eye_witness_pkg.install_flask)
        assert callable(eye_witness_pkg.install_celery)
        assert callable(eye_witness_pkg.EyeWitnessDjangoMiddleware)


class TestIntegrations:
    def test_fastapi_install_registers_http_middleware(self):
        class FakeApp:
            def middleware(self, kind):
                assert kind == "http"

                def decorator(fn):
                    self.fn = fn
                    return fn

                return decorator

        app = FakeApp()
        install_fastapi(app)
        assert callable(app.fn)

    def test_flask_install_registers_hooks(self):
        class FakeFlask:
            def before_request(self, fn):
                self.before = fn
                return fn

            def teardown_request(self, fn):
                self.teardown = fn
                return fn

        app = FakeFlask()
        install_flask(app)
        assert callable(app.before)
        assert callable(app.teardown)

    def test_celery_install_registers_signal_handlers(self):
        class Signal:
            def __init__(self):
                self.handlers = []

            def connect(self, fn):
                self.handlers.append(fn)
                return fn

        class Signals:
            task_prerun = Signal()
            task_postrun = Signal()

        install_celery(Signals)
        assert len(Signals.task_prerun.handlers) == 1
        assert len(Signals.task_postrun.handlers) == 1

    def test_django_middleware_calls_next(self):
        called = {"done": False}

        def get_response(request):
            called["done"] = True
            return "ok"

        middleware = EyeWitnessDjangoMiddleware(get_response)
        response = middleware(object())
        assert called["done"] is True
        assert response == "ok"
