# /core/observability.py

from __future__ import annotations

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.log.log import logger, START_MODULE_MESSAGE, str_object_is_created



MODULE_DESCRIPTION = "This module configures telemetry for the application"


_telemetry_configured = False
_delivery_messages_received_counter = None


def setup_telemetry(endpoint: str, service_name: str) -> None:
    """
    Configure OTEL tracing and metrics exporters once for the process.
    Конфигурирует экспортеры трассировки и метрик OTEL один раз для процесса.
        :parameter endpoint (str) - OTEL collector endpoint
        :parameter service_name (str) - name of the service to report
        :returns None
    """
    global _telemetry_configured
    if _telemetry_configured:
        return

    resource = Resource.create({"service.name": service_name})

    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)),
    )
    trace.set_tracer_provider(trace_provider)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint),
        export_interval_millis=1000,
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    _telemetry_configured = True


def instrument_app(app: FastAPI) -> None:
    """
    Attach OTEL instrumentation to FastAPI.
    Присоединяет инструментирование OTEL к FastAPI.
        :parameter app (FastAPI) - FastAPI application to instrument
        :returns None
    """
    FastAPIInstrumentor.instrument_app(app)


def get_delivery_messages_received_counter():
    """
    Return a singleton counter instrument for delivery_messages_received_total.
    Safe to call multiple times; the counter will be created once.
    """
    global _delivery_messages_received_counter
    if _delivery_messages_received_counter is not None:
        return _delivery_messages_received_counter

    meter = metrics.get_meter(__name__)
    counter = meter.create_counter(
        "delivery_messages_received_total",
        description="Total number of delivery messages received",
    )
    _delivery_messages_received_counter = counter
    return _delivery_messages_received_counter


def main() -> None:
    logger.info(START_MODULE_MESSAGE + str(__file__))
    logger.info(MODULE_DESCRIPTION)
    logger.info(str_object_is_created(setup_telemetry))
    logger.info(str_object_is_created(instrument_app))


if __name__ != "__main__":
    main()


if __name__ == "__main__":
    main()
