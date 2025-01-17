# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1.dev3] - 2025-01-17
### Added
- Added logging configuration support for the logging system
- Added LogConfig class for centralized color and formatting configuration
- Added environment-aware color support for terminal vs non-terminal environments
- Added automatic TTY detection for proper color handling
- Added file output formatting without ANSI color codes

### Changed
- Updated client classes to use dynamic logging configuration based on the module name
- Moved color configuration from LogFormatter to LogConfig class
- Separated console and file formatter logic for better maintainability
- Improved logging setup to handle both string and numeric log levels

### Fixed
- Fixed color bleeding in log files by properly handling non-terminal outputs
- Fixed handler cleanup to prevent duplicate log entries
- Fixed module name handling in get_logger for consistent logger hierarchy

## [0.2.1.dev2] - 2025-01-16

### Fixed
- Fixed issue where ClientFactory was not exposed in the package root.

## [0.2.1.dev1] - 2025-01-16

### Added
- Added list_drive_names method to ReadClient.
- Renamed `list_drives` method to `list_drives_and_root_contents` to more appropriately describe what the method does.
- Added comprehensive logging to BaseClient, CreateClient, and ReadClient.
- Added business-focused logging messages for better operational visibility.
- Added logging configuration examples in the examples directory.

### Fixed
- Fixed inconsistent logging levels across clients.
- Fixed handler cleanup in logging setup.
- Fixed missing logging in file operations.

### Changed
- Updated logging format for better readability.
- Standardized logging patterns across all client classes.
- Improved error message clarity for business users.



## [0.2.0.dev1] - 2025-01-14

### Added
- WRITE operations:
  - Upload files to SharePoint
  - Create lists
  - Create document libraries
  - Create folders


### Improved
- Refactored existing SharePointClient class.
  - As project scaled, it became apparent that the client class was becoming too large and complex.
  - This refactoring splits the client class into smaller, more manageable classes (BaseClient, CreateClient, ReadClient).
  - Removed utils module and moved functions to BaseClient.
- Improved existing test suite



## [0.1.0.dev1] - 2024-01-03

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


## Roadmap

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
