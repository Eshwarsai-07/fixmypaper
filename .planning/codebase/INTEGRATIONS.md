# External Integrations

## 1. Services

| Service | Protocol | Purpose | Dependency |
| :--- | :--- | :--- | :--- |
| **Grobid** | HTTP/JSON | Structured academic parsing (TEI XML) | `grobid-client-python` |
| **Reference API** | HTTP/REST | Likely used for citation/reference validation | `REFERENCE_API_URL` (Env) |

## 2. File System

- **Upload Folder:** `uploads/` - Stores raw user PDFs.
- **Processed Folder:** `processed/` - Stores annotated PDFs and extracted JSON data.
- **Local JSON Data:** `backend/formats.json` - Configuration for formatting rules and check logic.

## 3. Communication Patterns

- **Frontend -> Backend:**
  - POST `/upload`: File upload and processing trigger.
  - GET `/api/formats`: Fetch available formatting rules.
  - GET `/download/{job_id}`: Retrieve processed results.
- **Internal:**
  - `process_pdf` orchestrates multiple Python libraries (fitz, Camelot, Grobid) to generate annotations and statistics.

---
*Last Updated: 2026-04-19*
