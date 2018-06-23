import json
import logging
import sys

import pytest
import structlog

from iterio_commons.logging_setup import log_uncaught_exception, set_up_logging


@pytest.fixture(scope='function', autouse=True)
def reset_logging_setup():
    yield
    root_logger = logging.root
    handlers = root_logger.handlers.copy()
    filters = root_logger.filters.copy()
    for handler in handlers:
        root_logger.removeHandler(handler)
    for filter_ in filters:
        root_logger.removeFilter(filter_)


def test_logging_setup_with_std_logging(capsys):
    set_up_logging()

    log = logging.getLogger('test_log_1')
    log.info('info %s', 'inf')
    log.debug('debug %s', 'deb')
    log.error('error %s', 'err')
    try:
        raise ValueError('whatever')
    except ValueError:
        log.exception('exception %s', 'exc')

    out, err = capsys.readouterr()
    log_entries = [json.loads(line) for line in out.splitlines()]
    assert len(log_entries) == 3
    assert log_entries[0] == {'event': 'info inf', 'level': 'info', 'logger': 'test_log_1'}
    assert log_entries[1]['event'] == 'error err'
    assert log_entries[2]['event'] == 'exception exc'
    assert 'Traceback' in log_entries[2]['exception']
    assert not err


def test_logging_setup_with_structlog(capsys):
    set_up_logging()

    log = structlog.get_logger('test_log_2')
    log.info('info', some_value='inf')
    log.debug('debug', some_value='deb')
    log.error('error', some_value='err')
    try:
        raise ValueError('whatever')
    except ValueError:
        log.exception('exception', some_value='exc')

    out, err = capsys.readouterr()
    log_entries = [json.loads(line) for line in out.splitlines()]
    assert len(log_entries) == 3
    assert log_entries[0] == {
        'event': 'info',
        'some_value': 'inf',
        'level': 'info',
        'logger': 'test_log_2',
    }
    assert log_entries[1]['event'] == 'error'
    assert log_entries[2]['event'] == 'exception'
    assert 'Traceback' in log_entries[2]['exception']
    assert not err


def test_rendering_uncaught_errors(capsys):
    set_up_logging()

    try:
        raise ValueError('something!')
    except ValueError:
        log_uncaught_exception(*sys.exc_info())

    out, _ = capsys.readouterr()
    log_entry = json.loads(out)
    assert log_entry['event'] == 'Uncaught error'
    assert log_entry['level'] == 'error'
