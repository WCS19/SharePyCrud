# Logging in the `sharepycrud` Package

The `sharepycrud` Python package implements a robust and configurable logging mechanism to provide detailed insights into the application's behavior. This document outlines the logging architecture, its purpose, and how it operates across the different layers of the package.

## **Logging Overview**

The `logger.py` module centralizes the logging configuration for the entire package. It ensures that logs are consistent, informative, and easy to debug. The logging is divided into two primary responsibilities:
1. **Core Errors and HTTP-Level Issues:** Handled by the `BaseClient`.
2. **Business Logic-Specific Logging:** Managed in the `CreateClient` and `ReadClient` layers.

---

## **Logger Configuration**

### **Key Features**
- **Environment-Aware Logging:**
  The logging system automatically adapts to different environments (terminal vs non-terminal, file vs console) and adjusts formatting accordingly.

- **Custom Log Formatting:**
  The `LogConfig` class provides centralized configuration for log formatting, including:
  - Color-coded output for terminal environments
  - Plain text for file outputs and non-terminal environments
  - Consistent formatting across all logging methods

- **Log Levels:**
  [Previous content remains]

- **Output Options:**
  [Previous content remains]

- **Reusable Logger:**
  [Previous content remains]

### **Setup**
The `setup_logging()` function provides environment-aware configuration:
- `level`: The minimum logging level (default is `INFO`).
- `log_file`: An optional file to which logs can be written. (default is `None`)
- `use_colors`: Enable/disable color output (automatically disabled for non-terminal environments). (default is `True`)

Example:

```python
from sharepycrud.logger import setup_logging

# Basic setup with color support (if in terminal)
setup_logging(level="INFO")

# Setp with file output and no color support
setup_logging(
    level="DEBUG",
    log_file="application.log",
    use_colors=False,
)
```

### **Using Logger in Modules**

```python
from sharepycrud.logger import get_logger

logger = get_logger(__name__)

# Example usage
logger.info("This is an info message")
logger.error("This is an error message")
```

### **Color Support**


### **Color Support**
The logging system automatically handles color support:
- Colors are enabled by default in terminal environments
- Colors are automatically disabled for:
  - File outputs
  - Non-terminal environments
  - When explicitly disabled via `use_colors=False`
  - **Note**: if `use_colors=True` is set, the color support is enabled regardless of the environment and will write to log file using the color codes.
