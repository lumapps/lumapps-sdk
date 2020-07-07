# Changelog

Notable changes to this project will be documented in this file.

## 1.0.5 (12 June 2020)

### Added

* Change build system and add a more complete documentation

## 1.0.4 (11 June 2020)

### Added

* Added `BaseClient.upload` method that takes any of the types supported by HTTPX (`IO[str]`, `IO[bytes]`, `str`, `bytes`) as the argument for file contents. Filesystem file paths can still be used by with `BaseClient.upload_call`.
