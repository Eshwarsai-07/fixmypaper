# Technology Stack

## 1. Core Systems

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend** | Python / FastAPI | 0.116.0+ | REST API, PDF processing orchestration |
| **Frontend** | React / Next.js | 14.2.0+ | User interface (App Router) |
| **Deployment** | Docker / Docker Compose | — | Containerization and orchestration |

## 2. Backend Tech

- **Framework:** FastAPI (Uvicorn as server)
- **PDF Processing:**
  - `PyMuPDF` (fitz): Text extraction and annotation.
  - `Camelot-py`: Table extraction.
  - `pix2text`: OCR and sophisticated text extraction (likely formula/math support).
- **Academic Parsing:**
  - `grobid-client-python`: For structured academic document parsing.
- **Data Handling:** `pandas`, `numpy`, `lxml`.
- **Utilities:** `python-multipart` (file uploads), `beautifulsoup4` (HTML/XML parsing).

## 3. Frontend Tech

- **Framework:** Next.js 14 (App Router).
- **Styling:** Tailwind CSS (configured via `tailwind.config.ts`/`postcss.config.js`).
- **Logic:** React Hooks, Server Components (implied by Next.js 14).

## 4. Development & Tooling

- **Entry Points:**
  - Backend: `backend/app.py`
  - Frontend: `frontend/app/page.tsx` (standard Next.js)
- **Port Mapping (Compose):**
  - Backend: `5001 -> 7860`
  - Frontend: `3000 -> 3000`

---
*Last Updated: 2026-04-19*
