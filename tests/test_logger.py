import logging
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from typing import Any, Generator
import pytest

from sharepycrud.logger import setup_logging, get_logger
from sharepycrud.loggerConfig import LogConfig, LogFormatter


@pytest.fixture
def caplog_debug_level(caplog: Any) -> Generator[None, None, None]:
    """Fixture that ensures caplog is capturing at DEBUG level for all tests."""
    caplog.set_level(logging.DEBUG, logger="sharepycrud")
    yield


def test_get_logger_with_module_name() -> None:
    """Test get_logger with different module names."""
    logger1 = get_logger("test_module")
    assert logger1.name == "sharepycrud.test_module"

    logger2 = get_logger("sharepycrud.test_module")
    assert logger2.name == "sharepycrud.test_module"


def test_setup_logging_default(caplog: Any) -> None:
    """Test setup_logging with default parameters."""
    caplog.set_level(logging.DEBUG)

    # Reset any existing handlers
    root_logger = logging.getLogger("sharepycrud")
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    setup_logging()

    assert len(root_logger.handlers) == 1, "Expected exactly one console handler"

    test_logger = get_logger()
    test_logger.debug("Debug message - should not appear in caplog since level=INFO")
    test_logger.info("Info message - should appear in caplog")

    assert "Debug message - should not appear" not in caplog.text
    assert "Info message - should appear" in caplog.text


def test_setup_logging_with_file(tmp_path: Any, caplog_debug_level: None) -> None:
    """Test setup_logging with a file path."""
    log_file_path = tmp_path / "test_log.log"

    root_logger = logging.getLogger("sharepycrud")
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    setup_logging(level="WARNING", log_file=str(log_file_path))

    test_logger = get_logger()
    assert len(root_logger.handlers) == 2, "Expected console and file handlers"

    test_logger.warning("Warning message in file and console")

    with open(log_file_path, "r") as f:
        contents = f.read()
        assert "Warning message in file and console" in contents


def test_setup_logging_removes_existing_handlers(caplog: Any) -> None:
    """Test that setup_logging removes existing handlers before adding new ones."""
    root_logger = logging.getLogger("sharepycrud")

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add multiple handlers
    handler1 = logging.StreamHandler()
    handler2 = logging.StreamHandler()
    root_logger.addHandler(handler1)
    root_logger.addHandler(handler2)

    assert len(root_logger.handlers) == 2, "Expected two handlers before setup"

    setup_logging()

    assert len(root_logger.handlers) == 1, "Expected exactly one handler after setup"
    assert handler1 not in root_logger.handlers, "Old handler should be removed"
    assert handler2 not in root_logger.handlers, "Old handler should be removed"


def test_get_console_formatter_with_colors() -> None:
    """Test console formatter creation with colors enabled."""
    with patch("sys.stdout.isatty", return_value=True):
        formatter = LogConfig.get_console_formatter(use_colors=True)
        assert isinstance(formatter, LogFormatter)
        assert formatter.colors == LogConfig.COLORS
        assert formatter._fmt == "%(asctime)s %(name)s %(levelname)s - %(message)s"


def test_get_console_formatter_without_colors() -> None:
    """Test console formatter creation with colors disabled."""
    formatter = LogConfig.get_console_formatter(use_colors=False)
    assert isinstance(formatter, logging.Formatter)
    assert not isinstance(formatter, LogFormatter)
    assert formatter._fmt == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def test_log_formatter_initialization() -> None:
    """Test LogFormatter initialization with different parameters."""
    # Test with all parameters
    custom_colors = {"ERROR": "\033[31m"}
    formatter = LogFormatter(
        fmt="%(levelname)s: %(message)s", datefmt="%Y-%m-%d", colors=custom_colors
    )
    assert formatter.colors == custom_colors
    assert formatter._fmt == "%(levelname)s: %(message)s"

    # Test without optional parameters
    formatter_no_params = LogFormatter()
    assert formatter_no_params.colors == {}


def test_log_formatter_color_formatting() -> None:
    """Test that LogFormatter correctly applies color formatting."""
    formatter = LogFormatter(fmt="%(levelname)s: %(message)s", colors=LogConfig.COLORS)

    # Create a test record
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Test with TTY available
    with patch("sys.stderr.isatty", return_value=True):
        formatted = formatter.format(record)
        expected_color = LogConfig.COLORS["ERROR"]
        expected_reset = LogConfig.COLORS["RESET"]
        assert f"{expected_color}ERROR{expected_reset}" in formatted
        assert "Test message" in formatted


def test_log_formatter_no_color_when_no_tty() -> None:
    """Test that LogFormatter doesn't apply colors when not in a TTY."""
    formatter = LogFormatter(fmt="%(levelname)s: %(message)s", colors=LogConfig.COLORS)

    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Test without TTY
    with patch("sys.stderr.isatty", return_value=False):
        formatted = formatter.format(record)
        assert "\033[" not in formatted  # No ANSI color codes
        assert "ERROR: Test message" in formatted


def test_log_formatter_unknown_level() -> None:
    """Test LogFormatter behavior with unknown log level."""
    formatter = LogFormatter(
        fmt="%(levelname)s: %(message)s",
        colors={"INFO": "\033[32m"},  # Only define INFO color
    )

    # Create record with custom level
    record = logging.LogRecord(
        name="test",
        level=logging.CRITICAL,  # Level not in colors dict
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    with patch("sys.stderr.isatty", return_value=True):
        formatted = formatter.format(record)
        assert "CRITICAL: Test message" in formatted
