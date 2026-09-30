# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-30

### Changed

- LICENSE to License.txt
- Switched to packaging with Hatchling, uv, and versions from git tags
- Updated pre-commit hooks for Ruff
- Updated README
- Updated .gitignore

### Added

- GitHub Actions to run pytest on push and pull requests to the main branch, with mock cli test
- Contribution guide
- Changelog file
- Added deps.py as a way to check for installed dependency groups
- Cloud module with Nextcloud support (`gselib[cloud]`) — REST API client (`NextcloudClient`) and `occ` runner (`NextcloudOCC`) for managing external storage and shares
- CLI subcommand `gselib cloud nextcloud` for storage and share management via flags or environment variables
- Tests for the cloud module (client, OCC runner, and CLI dispatch)
- CI matrix extended to macOS and Windows

### Fixed

- `NextcloudOCC.__exit__` missing required exception arguments
- Version removed from CLI arguments and shown in the description instead

### Removed

- maps.py (no longer supported)
- paths.py (no longer supported)
- trajectory.py (no longer supported)
- version.py (no longer supported)
- .static-version (no longer supported)
