# Logging in the `sharepycrud` Package

The `sharepycrud` Python package implements a robust and configurable logging mechanism to provide detailed insights into the application's behavior. This document outlines the logging architecture, its purpose, and how it operates across the different layers of the package.

## **Logging Overview**

The `logger.py` module centralizes the logging configuration for the entire package. It ensures that logs are consistent, informative, and easy to debug. The logging is divided into two primary responsibilities:
1. **Core Errors and HTTP-Level Issues:** Handled by the `BaseClient`.
2. **Business Logic-Specific Logging:** Managed in the `CreateClient` and `ReadClient` layers.

---

## **Logger Configuration**

### **Key Features**
- **Custom Log Formatting:**
  The `LogFormatter` class formats log messages, adding optional color coding for different log levels when outputting to the terminal. This makes it easier to distinguish between log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

- **Log Levels:**
  Logging levels can be configured (e.g., `DEBUG`, `INFO`, `ERROR`), allowing developers to control the verbosity of logs.

- **Output Options:**
  Logs can be directed to the console, a file, or both, based on the configuration.

- **Reusable Logger:**
  A shared logger instance is available throughout the package using `get_logger()`.

### **Setup**
The `setup_logging()` function allows flexible configuration of logging parameters:
- `level`: The minimum logging level (default is `INFO`).
- `log_file`: An optional file to which logs can be written.
- `log_format`: A customizable format string for log messages.

Example:
```python
from sharepycrud.logger import setup_logging

setup_logging(
    level="DEBUG",
    log_file="application.log",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```
