# Testing Practices

## 1. Backend Testing

Current testing is primarily integration-based and manual.

- **Sample Test Script:** `test_sample.py`
  - Functionality: Programmatically creates a PDF with known formatting errors and runs the processor against it.
  - Verification: Prints detected errors and saves an annotated PDF for visual inspection.
- **Health Checks:** `/health` endpoint available for container orchestration (Docker healthchecks).
- **Manual Verification:** Developers run `docker compose up` and manually test the `/upload` flow.

## 2. Frontend Testing

- **Linting:** `eslint` configured (via `npm run lint`).
- **Build Validation:** Next.js build step (`npm run build`) ensures type safety (if TS) and route integrity.

## 3. Recommended Gaps

- **Unit Tests:** No `pytest` suite for individual `_check_*` functions in `pdf_processor.py`.
- **UI Tests:** No Playwright/Cypress tests for the upload and result visualization flow.
- **API Tests:** No automated tests for the CRUD operations on `formats.json`.

---
*Last Updated: 2026-04-19*
