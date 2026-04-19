# Roadmap: FixMyPaper

## Overview

The journey from a monolithic proof-of-concept to a scalable, production-grade research paper formatting platform.

## Phases

- [x] **Phase 0: Grounding** - Initial codebase mapping and GSD workflow setup. (Completed)
- [ ] **Phase 1: Modular Refactor** - Split the 2700-line `pdf_processor.py` into a check-based architecture.
- [ ] **Phase 2: Persistence Layer** - Replace in-memory state with a database for result tracking.
- [ ] **Phase 3: Security & Access** - Implement authentication and production-grade API configurations.

## Phase Details

### Phase 1: Modular Refactor
**Goal**: Improve maintainability by decoupling validation logic from extraction logic.
**Depends on**: Nothing
**Requirements**: SCAL-02
**Success Criteria**:
  1. `pdf_processor.py` is under 500 lines, serving as an orchestrator.
  2. Individual checks (e.g., Roman Headers, Fig Captions) live in separate files in `backend/checks/`.
  3. Existing `test_sample.py` passes without modification to its external interface.
**Plans**: 2 plans (Refactor structure, Migrate checks)

### Phase 2: Persistence Layer
**Goal**: Enable job tracking and history that survives server restarts.
**Depends on**: Phase 1
**Requirements**: SCAL-01
**Success Criteria**:
  1. A database (SQLite/PostgreSQL) is integrated into the backend.
  2. The `/results/{job_id}` endpoint pulls from the database.
  3. A new `/api/history` endpoint exists to list recent jobs.
**Plans**: 2 plans (Schema design, Migration of `processing_results`)

### Phase 3: Security & Access
**Goal**: Secure the platform for multi-user/public deployment.
**Depends on**: Phase 2
**Requirements**: AUTH-01, AUTH-02
**Success Criteria**:
  1. Middleware enforces API key or JWT authentication for "Professor Mode" actions.
  2. CORS settings are configurable and restricted to the frontend origin.
  3. File cleanup job exists to prevent disk exhaustion.
**Plans**: 2 plans (Auth implementation, Rate limiting/Lifecycle)

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Grounding | 1/1 | Complete | 2026-04-19 |
| 1. Modular Refactor | 0/2 | Not started | - |
| 2. Persistence Layer | 0/2 | Not started | - |
| 3. Security & Access | 0/2 | Not started | - |

---
*Last updated: 2026-04-19 after initialization*
