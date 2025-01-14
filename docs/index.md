# SharePyCrud Package
[![Version](https://img.shields.io/badge/version-0.2.0.dev1-blue)](#)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Tests Status](https://github.com/WCS19/SharePyCrud/actions/workflows/python-app.yml/badge.svg)
[![codecov](https://codecov.io/gh/WCS19/SharePyCrud/branch/main/graph/badge.svg?token=<CODECOV_TOKEN>)](https://codecov.io/gh/WCS19/SharePyCrud)



This package is a Python library for SharePoint CRUD operations. The package is currently in development with only **read** and **write** operations implemented. Update and Delete operations are under development and will be added in future releases.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Setup Instructions](#setup-instructions)
3. [Contributing](#contributing)
4. [Documentation References](#documentation-references)
5. [Examples](#examples)
6. [Changelog](#changelog)
7. [Github Repository](https://github.com/WCS19/SharePyCrud)
8. [License](#license)


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

To use this package, follow the setup instructions provided in the [SETUP.md](setup.md) file. It includes step-by-step instructions to configure the package and set up your development environment.

---

## Contributing

We welcome contributions to SharePyCrud! Whether you're fixing bugs, adding new features, or improving documentation, your help is valuable. Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

---

## Documentation References

Below are useful references to help you understand and work with SharePyCrud:

1. [Microsoft Graph API Documentation](https://learn.microsoft.com/en-us/graph/)
2. [SharePoint REST API Documentation](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service)
3. [Python Requests Library](https://docs.python-requests.org/en/latest/)

These resources will provide background on the APIs and libraries used in this project.

---

## Examples

Use the `examples` directory to run existing examples of both read and write operations.

```bash
python examples/read_operations/list_drives.py
```

```bash
python examples/read_operations/list_sites.py
```

```bash
python examples/write_operations/nested_folder_file_upload.py
```

There are currently only examples for the read and write operations. Examples for the other operations will be added in future releases.


---

### Changelog
See the [CHANGELOG.md](CHANGELOG.md) file for the latest updates and planned features.

---

### Github Repository

Please visit the Github repository for all the latest code updates.

[SharePyCrud Github Repository](https://github.com/WCS19/SharePyCrud)

---

### License
This project is licensed under the [MIT License](https://github.com/WCS19/SharePyCrud/blob/main/LICENSE). You are free to use, modify, and distribute the code, provided proper attribution is given.

Thank you for using SharePyCrud! If you have any questions or suggestions, feel free to open an issue or contribute to the project.
