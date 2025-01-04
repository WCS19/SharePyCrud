# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-03

### Added
- Initial release of SharePyCrud package.
- READ operations:
  - List SharePoint sites
  - List drives within sites
  - Download files from SharePoint
- Configuration management:
  - Environment variable support
  - Dotenv file support
- Type hints and mypy support
- Comprehensive test suite
- CI/CD pipeline with GitHub Actions
- Black code formatting
- Pre-commit hooks for code quality

### Dependencies
- Python 3.11+ requirement
- Core dependencies:
  - requests==2.32.3
  - python-dotenv==1.0.1
  - dataclasses-json==0.6.7

## [0.1.1] - 2025-01-04

### Added
- Added CHANGELOG.md file
- Adjusting the README.md file


## Roadmap

### [0.2.0] - Planned
- CREATE operations:
  - Create lists
  - Create document libraries
  - Create folders
  - Upload files
- Improved error handling
- Additional authentication methods

### [0.3.0] - Planned
- UPDATE operations:
  - Update file metadata
  - Move/copy files
  - Update list items
- Batch operations support

### [0.4.0] - Planned
- DELETE operations:
  - Delete files
  - Delete folders
  - Delete list items
- Recursive delete support
- Soft delete options

### Future Considerations
- SharePoint search integration
- Enhanced logging and monitoring
