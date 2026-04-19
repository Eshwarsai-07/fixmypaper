# Coding Conventions

## 1. Python (Backend)

- **Framework:** FastAPI with Type Hints.
- **Naming:**
  - Variables/Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `SCREAMING_SNAKE_CASE`
- **Documentation:** Google-style docstrings for functions and classes.
- **Async:** Uses `async/await` for API routes. Long-running CPU-bound tasks (PDF processing) are wrapped in `run_in_threadpool` to avoid blocking the event loop.
- **Typing:** Explicit type annotations for function signatures and Typed Pydantic models for request/response bodies.

## 2. JavaScript / React (Frontend)

- **Framework:** Next.js 14 App Router.
- **Typing:** Noted as `page.jsx` (JavaScript), though some configurations suggest potentially JSX.
- **Styling:** Utility-first CSS using Tailwind CSS.
- **Components:** Functional components with React Hooks.

## 3. Error Handling

- **Backend:** Centralized exception handler in `app.py`. Processing errors return a `500` with a traceback snippet in development/logs.
- **PDF Processing:** Heuristic fallbacks (e.g., if GROBID fails, use PyMuPDF). Error instances are collected in a list rather than raising exceptions immediately.

---
*Last Updated: 2026-04-19*
