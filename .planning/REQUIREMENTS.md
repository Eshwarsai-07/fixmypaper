# Requirements: FixMyPaper

**Defined:** 2026-04-19
**Core Value:** Enable users to catch and fix complex academic formatting errors instantly before submission.

## v1 Requirements (Baseline Functional State)

These requirements reflect the existing functionality inferred from the brownfield codebase.

### PDF Ingestion & Extraction

- [x] **CORE-01**: User can upload PDF files up to 50MB. (Implemented in `app.py`)
- [x] **CORE-02**: System extracts title, authors, and abstract using GROBID metadata. (Implemented in `pdf_processor.py`)
- [x] **CORE-03**: System extracts text tokens and preserves coordinate mapping for annotation. (Implemented via GROBID/Tei)

### Formatting Compliance (IEEE)

- [x] **RULE-01**: Detect if section headings use Roman numerals (e.g. I. INTRODUCTION).
- [x] **RULE-02**: Detect sequential numbering gaps in Figures, Tables, and Equations.
- [x] **RULE-03**: Validate that Figure captions are placed BELOW the figure and Table captions are placed ABOVE.
- [x] **RULE-04**: Detect common writing issues (repeated words, informal pronouns, "et al." formatting).

### Output & Visualization

- [x] **OUTP-01**: System generates an annotated PDF with visual error highlights.
- [x] **OUTP-02**: System provides a JSON summary of findings (Error count, statistics, mandatory section presence).

### User Experience

- [x] **UX-01**: Professor Mode: Create and delete custom rule-sets (CRUD on `formats.json`).
- [x] **UX-02**: Student Mode: Select format and upload for quick checking.

## v2 Requirements (Targeted Improvements)

### Security & Access Control

- [ ] **AUTH-01**: Implement user authentication for "Professor Mode" actions.
- [ ] **AUTH-02**: Restrict API access via robust CORS and rate limiting.

### Scalability & Reliability

- [ ] **SCAL-01**: Migrate in-memory job state to a persistent database (PostgreSQL/SQLite).
- [ ] **SCAL-02**: Decouple logic from `pdf_processor.py` into a modular `checks/` package to manage monolithic file debt.
- [ ] **REL-01**: Implement retry logic and better error isolation for GROBID/Camelot failures.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multi-format support | Currently optimized for IEEE (others possible via custom formats but UI/logic focused on IEEE patterns). |
| Real-time Collaborative Editing | High complexity, not core to checking value. |
| Plagiarism Detection | Out of scope for a style/formatting checker. |

## Traceability

| Requirement | Category | Baseline Status |
|-------------|----------|-----------------|
| CORE-01 | Ingestion | Complete |
| CORE-02 | Extraction | Complete |
| RULE-01 | Compliance| Complete |
| OUTP-01 | Output | Complete |
| UX-01 | UI | Complete |
| AUTH-01 | Security | Pending |
| SCAL-01 | Arch | Pending |

**Coverage:**
- v1 requirements: 10 total
- Mapped to existing code: 10
- Unmapped (v1): 0 ✓

---
*Last updated: 2026-04-19 after initial codebase mapping*
