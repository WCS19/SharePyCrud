import logging
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from typing import Any, Generator, TextIO
import pytest

from sharepycrud.logger import (
    LogFormatter,
    setup_logging,
    get_logger,
)


@pytest.fixture
def caplog_debug_level(caplog: Any) -> Generator[None, None, None]:
    """
    Fixture that ensures caplog is capturing at DEBUG level for all tests.
    """
    caplog.set_level(logging.DEBUG, logger="sharepycrud")
    yield


def test_get_logger_singleton() -> None:
    """
    Ensure get_logger always returns the same logger instance.
    """
    logger1: logging.Logger = get_logger()
    logger2: logging.Logger = get_logger()
    assert logger1 is logger2, "Expected get_logger to return the same logger instance"


def test_setup_logging_default(caplog: Any) -> None:
    """
    Test setup_logging with default parameters.
    Ensures the logger is configured at INFO level and has one handler.
    """
    caplog.set_level(logging.DEBUG)  # Explicitly set the level to DEBUG

    # Reset any existing handlers
    for handler in get_logger().handlers[:]:
        get_logger().removeHandler(handler)

    setup_logging()  # Default level=INFO

    test_logger: logging.Logger = get_logger()
    # Should have exactly 1 handler (console handler)
    assert len(test_logger.handlers) == 1, "Expected exactly one console handler"

    test_logger.debug("Debug message - should not appear in caplog since level=INFO")
    test_logger.info("Info message - should appear in caplog")

    assert "Debug message - should not appear" not in caplog.text
    assert "Info message - should appear" in caplog.text


def test_setup_logging_str_level(caplog: Any) -> None:
    """
    Test setup_logging with a string level, e.g., 'DEBUG'.
    """
    caplog.set_level(logging.DEBUG)
    for handler in get_logger().handlers[:]:
        get_logger().removeHandler(handler)

    setup_logging(level="DEBUG")

    test_logger: logging.Logger = get_logger()
    assert len(test_logger.handlers) == 1

    test_logger.debug("Debug message - should appear because level=DEBUG")
    test_logger.info("Info message - should appear")

    assert "Debug message - should appear because level=DEBUG" in caplog.text
    assert "Info message - should appear" in caplog.text


def test_setup_logging_file_handler(tmp_path: Any, caplog_debug_level: None) -> None:
    """
    Test setup_logging with a file path for log_file.
    """
    log_file_path = tmp_path / "test_log.log"

    for handler in get_logger().handlers[:]:
        get_logger().removeHandler(handler)

    setup_logging(level=logging.WARNING, log_file=str(log_file_path))

    test_logger: logging.Logger = get_logger()
    # Expect 2 handlers: console + file
    assert len(test_logger.handlers) == 2

    test_logger.warning("Warning message in file and console")

    with open(log_file_path, "r") as f:
        contents: str = f.read()
        assert "Warning message in file and console" in contents


def test_setup_logging_stream_handler(caplog_debug_level: None) -> None:
    """
    Test setup_logging with a TextIO stream as log_file.
    """
    for handler in get_logger().handlers[:]:
        get_logger().removeHandler(handler)

    stream: TextIO = StringIO()

    setup_logging(level="ERROR", log_file=stream)
    test_logger: logging.Logger = get_logger()
    assert len(test_logger.handlers) == 2

    test_logger.error("Error message for both handlers")

    stream.seek(0)
    assert "Error message for both handlers" in stream.read()


def test_log_formatter_no_color(caplog_debug_level: None) -> None:
    """
    Test that no ANSI color codes are added if sys.stderr.isatty() returns False.
    """
    formatter: LogFormatter = LogFormatter("%(levelname)s: %(message)s")

    # Patch sys.stderr.isatty() to return False
    with patch.object(sys.stderr, "isatty", return_value=False):
        record: logging.LogRecord = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        formatted: str = formatter.format(record)
        # Not expecting ANSI codes (e.g. \033[) in the string
        assert "\033[" not in formatted, "Color codes should not appear when not a TTY"


def test_log_formatter_with_color(caplog_debug_level: None) -> None:
    """
    Test that ANSI color codes are included if sys.stderr.isatty() returns True.
    """
    formatter: LogFormatter = LogFormatter("%(levelname)s: %(message)s")

    with patch.object(sys.stderr, "isatty", return_value=True):
        record: logging.LogRecord = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        formatted: str = formatter.format(record)
        assert "\033[0;31m" in formatted, "Expected ANSI color code for ERROR level"
        assert "Test message" in formatted
