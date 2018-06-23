"""
Common Iterio logging setup.
"""

import logging
import sys

import structlog


def set_up_logging():
    """Setting up the logging so that all logs (from ``structlog`` and from the standard
    library's ``logging``) come out as JSON with all the available information (like logger name,
    log level, etc.).
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(_get_structured_handler_for_all_logs())
    _configure_structlog_logging()

    _make_third_party_loggers_less_chatty()
    sys.excepthook = log_uncaught_exception


def set_up_logging_for_a_lambda():
    """Does the same stuff as the standard ``set_up_logging``, but also removes the log handler
    that Lambda generously gives  us, because it duplicates the log messages
    and generally messes stuff up.
    """
    # Normally, in a Lambda there should be only one handler here, so it doesn't matter whether
    # we take the one at 0 or -1, but during the pytest tests another handler is added to logging
    # at the beginning of the list.
    lambda_handler = logging.root.handlers[-1]
    logging.root.removeHandler(lambda_handler)
    set_up_logging()


def log_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Logs a nice JSON with the rendered exception info.
    """
    structlog.get_logger().error(
        "Uncaught error",
        exc_info=(exc_type, exc_value, exc_traceback))


_BASE_PROCESSING_CHAIN = [
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]


def _get_structured_handler_for_all_logs():
    pre_chain = _BASE_PROCESSING_CHAIN
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=pre_chain
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    return console_handler


def _configure_structlog_logging():
    structlog_processors = (
        [structlog.stdlib.filter_by_level] +
        _BASE_PROCESSING_CHAIN +
        [structlog.stdlib.ProcessorFormatter.wrap_for_formatter]
    )

    structlog.configure(
        processors=structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        cache_logger_on_first_use=True
    )


def _make_third_party_loggers_less_chatty():
    logging.getLogger('botocore').setLevel(logging.WARNING)


# TODO create a set_up_logging_with_sentry function, that will do the same thing as
# set_up_logging, but will take config parameter. And will set up Sentry.
# The formatter for Raven should add a fingerprint based on the event if there's no fingerprint,
# maybe. We need to see how Sentry will behave with structured errors first.
