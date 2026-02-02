import os

import httpx
from fastapi import FastAPI
from starlette.responses import Response

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

otel_endpoint = os.getenv("OPENTELEMETRY__ENDPOINT", "http://otel-collector:4317")
service_b_url = os.getenv("SERVICE_B__URL", "http://service-b")

resource = Resource.create({"service.name": "service-amp"})

trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_endpoint)),
)
trace.set_tracer_provider(trace_provider)

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=otel_endpoint),
    export_interval_millis=1000,
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()


@app.post("/api/message-a")
async def message_a() -> dict[str, str]:
    async with httpx.AsyncClient(base_url=service_b_url) as client:
        response = await client.post("/api/message-b")
        response.raise_for_status()
    return {"status": "ok"}


@app.post("/api/error")
async def error(code: int = 500) -> Response:
    return Response(status_code=code)
