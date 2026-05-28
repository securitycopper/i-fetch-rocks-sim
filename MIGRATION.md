# Migration Plan

This document tracks migration from the existing i-fetch-rocks repository into this reusable package.

## Principles

- Keep this package focused on save parsing, graph/network reconstruction, simulation behavior, and general analysis APIs.
- Keep CPU-ship specific diagnostics and workflows in i-fetch-rocks-cpu-ship.
- Preserve behavior first, then refactor behind stable public APIs.

## Phase 1 - Foundations

- [x] Package scaffold and CI.
- [x] Initial public API placeholders.
- [x] Migrate wire network primitives:
  - DataNetwork
  - LargeDataNetwork
  - DataNetworkManager
- [x] Migrate label registry:
  - LabelRegistry
  - AmbiguousLabelError
- [x] Add unit tests for migrated primitives.

## Phase 2 - Save Loading Surface

- [ ] Migrate simulator save loader entry points.
- [ ] Add typed models for ship, rooms, and components.
- [ ] Expose stable APIs to inventory rooms, devices, and wires.
- [ ] Add fixture-based tests using representative save snippets.

## Phase 3 - Analysis APIs

- [ ] Migrate wire diff support.
- [ ] Migrate room-port inventory and save diff helpers.
- [ ] Migrate optional tracing API with clear stability markers.

## Phase 4 - Optional Tick Simulation

- [ ] Port core device execution loop.
- [ ] Separate generic simulation hooks from game-specific CPU helpers.
- [ ] Add integration tests for deterministic tick behavior.

## Phase 5 - Release Readiness

- [ ] Finalize package naming and repository metadata.
- [ ] Add API docs and examples for third-party app developers.
- [ ] Publish 0.1 pre-release.
