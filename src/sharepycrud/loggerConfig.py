from typing import Dict, Optional
import logging
import sys


class LogConfig:
    """Configuration for sharepycrud logger."""

    COLORS: Dict[str, str] = {
        "DEBUG": "\033[0;36m",  # Cyan
        "INFO": "\033[0;32m",  # Green
        "WARNING": "\033[0;33m",  # Yellow
        "ERROR": "\033[0;31m",  # Red
        "CRITICAL": "\033[0;37;41m",  # White on Red
        "RESET": "\033[0m",  # Reset
    }

    @staticmethod
    def get_console_formatter(use_colors: bool = True) -> logging.Formatter:
        """Get a console formatter with optional color support."""
        if use_colors and sys.stdout.isatty():
            return LogFormatter(
                fmt="%(asctime)s %(name)s %(levelname)s - %(message)s",
                colors=LogConfig.COLORS,
            )
        return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    @staticmethod
    def get_file_formatter() -> logging.Formatter:
        """Get a file formatter (no color support)."""
        return logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


class LogFormatter(logging.Formatter):
    """Custom formatter with optional color support."""

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.colors = colors or {}

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with optional color coding."""
        if self.colors and sys.stderr.isatty():
            levelname = record.levelname
            if levelname in self.colors:
                record.levelname = (
                    f"{self.colors[levelname]}{levelname}{LogConfig.COLORS['RESET']}"
                )
        return super().format(record)
