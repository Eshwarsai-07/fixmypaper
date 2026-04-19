# Technical Concerns & Debt

## 1. Architectural Debt

- **Monolithic Processor:** `pdf_processor.py` is >2700 lines. The validation logic, extraction logic, and coordinate handling are all tightly coupled in one class/file.
- **State Management:** `app.py` uses an in-memory dictionary (`processing_results`) to store job results. This is lost on server restart and prevents scaling to multiple container instances without a shared database/store.
- **Resource Intensity:** PDF processing is CPU/Memory intensive (especially with Camelot and Grobid integration). Current `run_in_threadpool` approach is vulnerable to "noisy neighbor" issues under load. Needs a task queue (e.g., Celery/Redis).

## 2. Security Patterns

- **CORS:** Currently set to `allow_origins=["*"]`. Should be restricted to the frontend domain in production.
- **Authentication:** No auth layer exists for the `/upload` or `/api/formats` endpoints. Any user can create/delete formatting rules.
- **File Lifecycle:** `uploads/` and `processed/` files are not automatically cleaned up in the current code, which will eventually exhaust disk space.

## 3. Reliability & Edge Cases

- **GROBID Dependency:** The system heavily depends on an external/internal GROBID instance. If unavailable, many structural checks are skipped or fall back to weaker heuristics.
- **Complex Layouts:** Multi-column PDFs or those with non-standard fonts may still cause coordinate-offset issues in the annotation layer.
- **Performance:** Table extraction (Camelot) can be very slow on scanned PDFs or large documents.

---
*Last Updated: 2026-04-19*
