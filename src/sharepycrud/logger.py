import sys
import logging
from typing import Optional, Union, TextIO, Dict, ClassVar, Any
from sharepycrud.loggerConfig import LogConfig


def setup_logging(
    level: Union[int, str] = "INFO",
    log_file: Optional[str] = None,
    use_colors: bool = True,
) -> None:
    """Configure package-wide logging settings with environment aware settings."""

    root_logger = logging.getLogger("sharepycrud")

    # Handle level setting with proper type checking
    if isinstance(level, str):
        numeric_level = getattr(logging, level.upper())
    else:
        numeric_level = level

    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        LogConfig.get_console_formatter(use_colors and sys.stdout.isatty())
    )
    root_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(LogConfig.get_file_formatter())
        root_logger.addHandler(file_handler)


def get_logger(module_name: str = __name__) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        module_name: The name of the module requesting the logger (default: __name__)

    Returns:
        A logger instance configured for the specified module
    """
    if module_name.startswith("sharepycrud"):
        logger_name = module_name
    else:
        logger_name = f"sharepycrud.{module_name}"
    return logging.getLogger(logger_name)
