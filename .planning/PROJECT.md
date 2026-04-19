# FixMyPaper — Research Paper Formatter Checker

## What This Is

FixMyPaper is a tool designed to help researchers and students ensure their papers comply with specific academic formatting guidelines (initially IEEE). It analyzes PDF uploads using semantic parsing (GROBID) and heuristic checks (PyMuPDF/Camelot) to identify style violations and formatting errors, providing an annotated PDF with visual highlights of the issues.

## Core Value

Enable users to catch and fix complex academic formatting errors instantly before submission, reducing desk rejects and manual proofreading time.

## Requirements

### Validated

- ✓ **PDF Ingestion** — Support uploading and parsing PDFs up to 50MB.
- ✓ **Semantic Extraction** — Identification of title, authors, abstract, and section headings via GROBID TEI XML.
- ✓ **Rule Validation** — Detection of roman numeral headings, sequential numbering (figs/tables/refs), and caption placement.
- ✓ **Interactive Annotations** — Generation of a results PDF with highlighted error instances.
- ✓ **Persona-based Views** — "Professor" mode for managing formats and "Student" mode for quick checking.
- ✓ **Custom Formats** — JSON-based persistence of formatting rule profiles (`formats.json`).

### Active

- [ ] **Technical Debt Reduction** — Refactor `pdf_processor.py` for better maintainability.
- [ ] **Scalability Support** — Replace in-memory result storage with persistent storage or a database.
- [ ] **Deployment Reliability** — Stabilize GROBID integration and improve error handling for extraction failures.
- [ ] **User Objective** — [Awaiting specific user task for this session]

### Out of Scope

- **Direct PDF Editing** — The tool highlights errors but does not allow text editing within the PDF itself.
- **Plagiarism Detection** — Focused strictly on formatting, style, and structure.

## Context

- **Tech Stack:** FastAPI, Next.js, Docker Compose, GROBID, PyMuPDF.
- **Environment:** High dependency on Grobid for semantic structure; fallbacks exist but are less precise.
- **Development State:** Existing functional prototype with significant monolithic logic in the backend.

## Constraints

- **Dependency**: GROBID — Semantic structure checks are only as good as the Grobid parsing layer.
- **Performance**: PDF processing with OCR and table extraction is CPU-intensive.
- **Security**: Current API lacks authentication and has open CORS settings.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **GROBID for Parsing** | TEI XML provides better structural guarantees than raw PDF text proximity. | ✓ Good |
| **PyMuPDF for Annotation** | Best-in-class for writing highlights and comments back to existing PDF coordinate space. | ✓ Good |
| **JSON formats.json** | Simple persistence for rule sets without requiring a full DB for MVP. | ⚠️ Revisit |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-19 after initialization*
