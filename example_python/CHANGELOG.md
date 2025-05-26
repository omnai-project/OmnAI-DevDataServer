## Changelog 

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-05-26

### Added
- Introduced **API versioning**; all endpoints now live under **`/v1/…`**.
- Introduced CORS rule to grant access to the server APIs for browser applications running on **`http://localhost:4200`** 

### Changed
**BREAKING CHANGE**  
  - REST: `/UUID` → `/v1/get_devices`  
  - WebSocket: `/ws` → `/v1/subscribe_ws`

### Removed
- Deprecated un-versioned endpoints (`/UUID`, `/ws`).


