## Changelog 

- This changelog keeps track of all breaking changes. It does NOT include other changes. 

## [Unreleased] - 2025-05-23

### Added
- Introduced **API versioning**; all endpoints now live under **`/v1/…`**.

### Changed
**BREAKING CHANGE**  
  - REST: `/UUID` → `/v1/get_devices`  
  - WebSocket: `/ws` → `/v1/subscribe_ws`

### Removed
- Deprecated un-versioned endpoints (`/UUID`, `/ws`).


