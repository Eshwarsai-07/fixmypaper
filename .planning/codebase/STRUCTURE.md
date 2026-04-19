# Directory Structure

```text
fixmypaper/
├── .planning/              # GSD workflow docs
│   └── codebase/           # Codebase analysis (You are here)
├── backend/                # FastAPI Application
│   ├── app.py              # Main API entry point & routes
│   ├── pdf_processor.py    # Core business logic (Validation Engine)
│   ├── pix2text_processor.py # Math/OCR integration logic
│   ├── formats.json        # Rule definitions & custom formats
│   └── grobid_outputs/     # (Generated) Cached TEI XML results
├── frontend/               # Next.js 14 Application
│   ├── app/                # App Router files
│   │   ├── professor/      # Professor dashboard (Custom formats)
│   │   ├── student/        # Student upload & result view
│   │   ├── upload/         # Common upload components
│   │   ├── layout.jsx      # Global layout
│   │   └── page.jsx        # Landing page
│   ├── components/         # Reusable UI components
│   ├── public/             # Static assets
│   ├── Dockerfile          # Frontend container build
│   └── package.json        # Node dependencies
├── docs/                   # Documentation (Deployment, Manuals)
├── processed/              # (Ignored) Annotated output files
├── scripts/                # Utility scripts (Setup, Deploy)
├── uploads/                # (Ignored) Temporary uploaded PDFs
├── docker-compose.yml      # Service orchestration
├── Dockerfile.backend      # Backend container build
└── requirements.txt        # Python dependencies
```

## Key Modules

- **`backend/pdf_processor.py`**: Contains the `PDFErrorDetector` class and `AVAILABLE_CHECKS` dictionary.
- **`backend/app.py`**: FastAPI app using `APIRouter`. Handles CORS and exception mapping.
- **`frontend/app/page.jsx`**: Main navigation hub.

---
*Last Updated: 2026-04-19*
