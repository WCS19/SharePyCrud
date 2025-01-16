import sys
import logging
from typing import Optional, Union, TextIO, Dict, ClassVar, Any

logger: logging.Logger = logging.getLogger("sharepycrud")


class LogFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""

    COLORS: ClassVar[Dict[str, str]] = {
        "DEBUG": "\033[0;36m",  # Cyan
        "INFO": "\033[0;32m",  # Green
        "WARNING": "\033[0;33m",  # Yellow
        "ERROR": "\033[0;31m",  # Red
        "CRITICAL": "\033[0;37;41m",  # White on Red
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with optional color coding.

        Args:
            record: The log record to format

        Returns:
            The formatted log string
        """
        # Add colors if log message is going to a terminal
        if sys.stderr.isatty():
            levelname: str = record.levelname
            record.levelname = (
                f"{self.COLORS.get(levelname, '')}"
                f"{levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)


def setup_logging(
    level: Union[int, str] = logging.INFO,
    log_file: Optional[Union[str, TextIO]] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> None:
    """
    Configure package-wide logging settings.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path or file object to write logs to
        log_format: Format string for log messages

    Returns:
        None
    """
    # Convert string level to integer if necessary
    numeric_level: int
    if isinstance(level, str):
        numeric_level = getattr(logging, level.upper())
    else:
        numeric_level = level

    logger.setLevel(numeric_level)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter: LogFormatter = LogFormatter(log_format)

    console_handler: logging.StreamHandler[Any] = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file is not None:
        file_handler: Union[logging.FileHandler, logging.StreamHandler[Any]]
        if isinstance(log_file, str):
            file_handler = logging.FileHandler(log_file)
        else:
            file_handler = logging.StreamHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logger() -> logging.Logger:
    """
    Get the package logger.

    Returns:
        The configured package logger
    """
    return logger
