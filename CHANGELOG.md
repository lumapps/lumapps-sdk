# Changelog

Notable changes to this project will be documented in this file.

## 1.0.4 (11 June 2020)

### Added

* Added `ApiClient.upload` method that takes any of the types supported by HTTPX (`IO[str]`, `IO[bytes]`, `str`, `bytes`) as the argument for file contents. Filesystem file paths can still be used by with `ApiClient.upload_call`.
