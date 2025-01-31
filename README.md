# SharePyCrud Package
[![Version](https://img.shields.io/badge/version-0.2.1.dev4-blue)](#)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Tests Status](https://github.com/WCS19/SharePyCrud/actions/workflows/python-app.yml/badge.svg)
[![codecov](https://codecov.io/gh/WCS19/SharePyCrud/branch/main/graph/badge.svg)](https://codecov.io/gh/WCS19/SharePyCrud)
[![Documentation Status](https://readthedocs.org/projects/sharepycrud/badge/?version=latest)](https://sharepycrud.readthedocs.io/en/latest/)




This package is a Python library for SharePoint CRUD operations. The package is currently in development with only **read** and **write** operations implemented. Update and Delete operations are under development and will be added in future releases.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Setup Instructions](#setup-instructions)
3. [Architecture](#architecture)
4. [Logging System](#logging-system)
5. [Contributing](#contributing)
6. [Documentation References](#documentation-references)
7. [Examples](<https://github.com/WCS19/SharePyCrud/tree/main/examples> "Examples Directory")
8. [Changelog](#changelog)
9. [ReadTheDocs Documentation](#readthedocs-documentation)
10. [License](#license)


---

## Introduction

SharePyCrud simplifies interaction with SharePoint for CRUD (Create, Read, Update, Delete) operations by providing an intuitive Python API. It's designed to handle common SharePoint tasks, such as:

- Accessing files and folders in SharePoint document libraries.
- Downloading files in SharePoint sites.
- Creating folders and subfolders.
- Uploading files to SharePoint sites.
- Creating lists in SharePoint sites.
- Updating and deleting files (planned) and more!

---

## Setup Instructions

To use this package, follow the setup instructions provided in the [SETUP.md](docs/setup.md) file. It includes step-by-step instructions to configure the package and set up your development environment.

---

## Architecture

The package is designed to be modular and easy to understand. The [ARCHITECTURE.md](docs/ARCHITECTURE.md) file provides a detailed overview of the package's architecture and design.

---

## Logging System

SharePyCrud implements an environment-aware logging system that automatically adapts to different execution contexts. Key features include:

- Color-coded logs in terminal environments
- Automatic format adjustment for different outputs
- Module-specific logging support
- File and console output options

For detailed information about logging configuration and usage, see [LOGGING.md](docs/LOGGING.md).

---

## Contributing

We welcome contributions to SharePyCrud! Whether you're fixing bugs, adding new features, or improving documentation, your help is valuable. Please refer to the [CONTRIBUTING.md](docs/CONTRIBUTING.md) file for guidelines on how to contribute.

---

## Documentation References

Below are useful references to help you understand and work with SharePyCrud:

1. [Microsoft Graph API Documentation](https://learn.microsoft.com/en-us/graph/)
2. [SharePoint REST API Documentation](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service)
3. [Python Requests Library](https://docs.python-requests.org/en/latest/)
4. [Singleton Pattern in Python – A Complete Guide](https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/)
5. [The Singleton Pattern](https://python-patterns.guide/gang-of-four/singleton/)
6. [Python Logging Tutorial](https://docs.python.org/3/howto/logging.html)

These resources will provide background on the APIs, libraries and design patterns used in this project.

---

## Examples

Use the `examples` directory to run existing examples of read operations.

```bash
python examples/read_operations/list_drives.py
```

```bash
python examples/read_operations/list_sites.py
```

```bash
python examples/write_operations/nested_folder_file_upload.py
```

There are currently only examples for the read operations. Examples for the other operations will be added in future releases.

---

### Changelog
See the [CHANGELOG.md](docs/CHANGELOG.md) file for the latest updates and planned features.

---

### ReadTheDocs Documentation

Please visit the ReadTheDocs page for all the latest documentation.

[SharePyCrud ReadTheDocs](https://sharepycrud.readthedocs.io/en/latest/)

---

### License
This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute the code, provided proper attribution is given.

Thank you for using SharePyCrud! If you have any questions or suggestions, feel free to open an issue or contribute to the project.
