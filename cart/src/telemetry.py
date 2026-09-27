import logging
from os import environ

from flask import Flask
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter as GrpcLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter as GrpcMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as GrpcSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter as HttpLogExporter,
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter as HttpMetricExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HttpSpanExporter,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy import Engine


def initTelemetry(app: Flask, engine: Engine) -> None:
    """Initializes OpenTelemetry tracing, metrics and logging.

    The OTLP exporter protocol is chosen through the
    OTEL_EXPORTER_OTLP_PROTOCOL environment variable ("grpc" or
    "http/protobuf"), and the collector endpoint through
    OTEL_EXPORTER_OTLP_ENDPOINT.
    """
    useHttp: bool = (
        environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc") == "http/protobuf"
    )
    endpoint: str = environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") or (
        "http://localhost:4318" if useHttp else "http://localhost:4317"
    )

    resource = Resource.create(
        {"service.name": environ.get("OTEL_SERVICE_NAME", "puc-arq-soft-cart")}
    )

    spanExporter = (
        HttpSpanExporter(endpoint=f"{endpoint}/v1/traces")
        if useHttp
        else GrpcSpanExporter(endpoint=endpoint)
    )
    tracerProvider = TracerProvider(resource=resource)
    tracerProvider.add_span_processor(BatchSpanProcessor(spanExporter))
    trace.set_tracer_provider(tracerProvider)

    metricExporter = (
        HttpMetricExporter(endpoint=f"{endpoint}/v1/metrics")
        if useHttp
        else GrpcMetricExporter(endpoint=endpoint)
    )
    meterProvider = MeterProvider(
        resource=resource,
        metric_readers=[PeriodicExportingMetricReader(metricExporter)],
    )
    metrics.set_meter_provider(meterProvider)

    logExporter = (
        HttpLogExporter(endpoint=f"{endpoint}/v1/logs")
        if useHttp
        else GrpcLogExporter(endpoint=endpoint)
    )
    loggerProvider = LoggerProvider(resource=resource)
    loggerProvider.add_log_record_processor(BatchLogRecordProcessor(logExporter))
    set_logger_provider(loggerProvider)
    logging.getLogger().addHandler(LoggingHandler(logger_provider=loggerProvider))

    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=engine)
