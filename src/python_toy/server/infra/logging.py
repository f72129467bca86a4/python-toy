from __future__ import annotations

import logging
from typing import cast

import structlog
from python_toy.server.infra.config import LoggingConfig


TIMESTAMP_KEY = "@timestamp"


def _setup_stdlog_adapter(
    config: LoggingConfig, timestamper: structlog.types.Processor, renderer: structlog.types.Processor
) -> None:
    pre_chain: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        timestamper,
        structlog.processors.add_log_level,
        structlog.stdlib.add_logger_name,
    ]

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=pre_chain,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # root 핸들러 재구성 (basicConfig 사용 대신 명시적 구성)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(config.level)


def _redirect_loggers() -> None:
    for name in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
    ]:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True


def setup(config: LoggingConfig) -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True, key=TIMESTAMP_KEY)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.contextvars.merge_contextvars,
            timestamper,
            structlog.processors.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # Delegate to stdlib
        ],
        wrapper_class=structlog.make_filtering_bound_logger(config.level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    renderer: structlog.types.Processor
    if config.format == "json":
        renderer = structlog.processors.JSONRenderer(sort_keys=True)
    elif config.format == "text":
        renderer = structlog.processors.KeyValueRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(timestamp_key=TIMESTAMP_KEY)

    _setup_stdlog_adapter(config, timestamper, renderer)
    _redirect_loggers()

    get_logger(__name__).info("logging.configured", config=config.model_dump())


def get_logger(name: str) -> structlog.BoundLogger:
    return cast(structlog.BoundLogger, structlog.get_logger(name))


__all__ = ("get_logger", "setup")
