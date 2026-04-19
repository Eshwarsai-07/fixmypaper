"""FastAPI application for Research Paper Error Checker."""
import json
import logging
import os
import shutil
import subprocess
import sys
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from werkzeug.utils import secure_filename

from backend.pdf_processor import ALL_SECTIONS, AVAILABLE_CHECKS
from backend.pipeline import run_validation_pipeline
from backend.validation_models import ValidationIssue, ValidationSummary

MAX_CONTENT_LENGTH = 50 * 1024 * 1024
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
FORMATS_FILE = Path(__file__).parent / "formats.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("fixmypaper-backend")

app = FastAPI(title="Research Paper Error Checker")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router = APIRouter()


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


class FormatCreateRequest(BaseModel):
    name: str
    created_by: str
    description: str = ""
    mandatory_sections: List[str] = Field(default_factory=list)
    enabled_checks: List[str] = Field(default_factory=list)


class FormatResponse(BaseModel):
    id: str
    name: str
    created_by: str
    is_system: bool = False
    description: str = ""
    mandatory_sections: List[str] = Field(default_factory=list)
    enabled_checks: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: str


class SuccessResponse(BaseModel):
    success: bool


class PageSummaryResponse(BaseModel):
    all_sections: Optional[List[str]] = None
    checks_by_cat: Dict[str, List[Any]]
    formats: Optional[List[Dict[str, Any]]] = None


class ErrorItem(BaseModel):
    check_id: str
    check_name: str
    description: str
    page_num: int
    text: str
    error_type: str


class DocumentOverview(BaseModel):
    title: str
    authors: str
    abstract: str
    key_insights: List[str]


class UploadResponse(BaseModel):
    job_id: str
    original_filename: str
    output_filename: str
    summary: ValidationSummary
    error_count: int
    errors: List[ValidationIssue]
    statistics: Dict[str, Any]
    reference_analysis: Dict[str, Any]
    mandatory_sections: List[str]
    document_overview: DocumentOverview
    start_page: int
    success: bool


class JobResult(BaseModel):
    job_id: str
    original_filename: str
    output_filename: str
    input_path: str
    output_path: str
    start_page: int
    summary: ValidationSummary
    errors: List[ValidationIssue]
    error_count: int
    statistics: Dict[str, Any]
    reference_analysis: Dict[str, Any]
    mandatory_sections: List[str]
    document_overview: DocumentOverview
    processed_at: str


class HealthResponse(BaseModel):
    status: str


processing_results: Dict[str, Dict[str, Any]] = {}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "pdf"


def _build_document_overview(
    extracted_data: Dict[str, Any],
    original_filename: str,
    statistics: Dict[str, Any],
    error_count: int,
) -> Dict[str, Any]:
    """Build a lightweight, UI-friendly summary from extracted data."""
    full_text = (extracted_data or {}).get("full_text", "") or ""
    lines = [ln.strip() for ln in full_text.splitlines() if ln.strip()]

    title = lines[0] if lines else original_filename
    authors = "Not detected"
    if len(lines) > 1 and len(lines[1]) < 140:
        authors = lines[1]

    abstract = "Not detected"
    abstract_idx = full_text.lower().find("abstract")
    if abstract_idx >= 0:
        snippet = full_text[abstract_idx : abstract_idx + 1200]
        parts = snippet.split("\n", 1)
        abstract_candidate = parts[1] if len(parts) > 1 else snippet
        abstract = " ".join(abstract_candidate.split())[:550] or "Not detected"

    stats = statistics or {}
    insights = [
        f"{error_count} formatting issue(s) detected",
        f"{stats.get('total_figures', 0)} figure(s) and {stats.get('total_tables', 0)} table(s) identified",
        f"{stats.get('total_equations', 0)} equation(s) detected",
    ]

    return {
        "title": title[:200],
        "authors": authors[:240],
        "abstract": abstract,
        "key_insights": insights,
    }


def load_formats() -> List[Dict[str, Any]]:
    if FORMATS_FILE.exists():
        with open(FORMATS_FILE, encoding="utf-8") as f:
            return json.load(f).get("formats", [])
    return []


def save_formats(formats: List[Dict[str, Any]]) -> None:
    with open(FORMATS_FILE, "w", encoding="utf-8") as f:
        json.dump({"formats": formats}, f, indent=2)


@router.get("/", response_model=PageSummaryResponse)
async def home() -> PageSummaryResponse:
    checks_by_cat: Dict[str, List[Any]] = {}
    for _, info in AVAILABLE_CHECKS.items():
        checks_by_cat.setdefault(info["category"], []).append(info["name"])
    return PageSummaryResponse(checks_by_cat=checks_by_cat)


@router.get("/professor", response_model=PageSummaryResponse)
async def professor() -> PageSummaryResponse:
    checks_by_cat: Dict[str, List[Any]] = {}
    for cid, info in AVAILABLE_CHECKS.items():
        checks_by_cat.setdefault(info["category"], []).append({"id": cid, **info})
    formats = await run_in_threadpool(load_formats)
    return PageSummaryResponse(
        all_sections=ALL_SECTIONS,
        checks_by_cat=checks_by_cat,
        formats=formats,
    )


@router.get("/student", response_model=PageSummaryResponse)
async def student() -> PageSummaryResponse:
    formats = await run_in_threadpool(load_formats)
    return PageSummaryResponse(checks_by_cat={}, formats=formats)


@router.get("/api/formats", response_model=List[FormatResponse])
async def list_formats() -> List[FormatResponse]:
    formats = await run_in_threadpool(load_formats)
    return [FormatResponse(**fmt) for fmt in formats]


@router.post("/api/formats", response_model=FormatResponse, status_code=201)
async def create_format(data: FormatCreateRequest) -> FormatResponse:
    if not data.name.strip() or not data.created_by.strip():
        raise HTTPException(status_code=400, detail="name and created_by are required")

    new_fmt = {
        "id": str(uuid.uuid4()),
        "name": data.name.strip(),
        "created_by": data.created_by.strip(),
        "is_system": False,
        "description": data.description.strip(),
        "mandatory_sections": data.mandatory_sections,
        "enabled_checks": data.enabled_checks,
    }
    formats = await run_in_threadpool(load_formats)
    formats.append(new_fmt)
    await run_in_threadpool(save_formats, formats)
    return FormatResponse(**new_fmt)


@router.delete(
    "/api/formats/{fmt_id}",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
)
async def delete_format(fmt_id: str) -> SuccessResponse:
    formats = await run_in_threadpool(load_formats)
    updated = [f for f in formats if f["id"] != fmt_id or f.get("is_system")]
    if len(updated) == len(formats):
        raise HTTPException(status_code=404, detail="Format not found or is a system format")
    await run_in_threadpool(save_formats, updated)
    return SuccessResponse(success=True)


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_file(
    file: UploadFile = File(...),
    format_id: str = Form(default=""),
    start_page: int = Form(default=1),
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    safe_start_page = max(1, start_page)
    required_sections: List[str] = []
    enabled_check_types: Optional[set[str]] = None

    if format_id:
        formats = await run_in_threadpool(load_formats)
        fmt = next((f for f in formats if f["id"] == format_id), None)
        if fmt:
            required_sections = fmt.get("mandatory_sections", [])
            enabled_checks = fmt.get("enabled_checks", [])
            if enabled_checks:
                types = {"missing_required_section"}
                for cid in enabled_checks:
                    if cid in AVAILABLE_CHECKS:
                        types.update(AVAILABLE_CHECKS[cid]["error_types"])
                enabled_check_types = types

    try:
        job_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, f"{job_id}_{original_filename}")
        output_filename = f"annotated_{original_filename}"
        output_path = os.path.join(PROCESSED_FOLDER, f"{job_id}_{output_filename}")

        data = await file.read()
        if len(data) > MAX_CONTENT_LENGTH:
            raise HTTPException(status_code=400, detail="File exceeds 50MB size limit")
        await run_in_threadpool(Path(input_path).write_bytes, data)

        logger.info(
            "[PROCESSING] job_id=%s file=%s size_bytes=%s format=%s start_page=%s",
            job_id,
            original_filename,
            len(data),
            format_id or "none",
            safe_start_page,
        )

        pipeline_success = True
        pipeline_error_message: Optional[str] = None
        errors: List[ValidationIssue] = []
        summary = ValidationSummary(errors=0, pages_with_errors=0, figures=0, tables=0)
        statistics: Dict[str, Any] = {}
        extracted_data: Dict[str, Any] = {}
        reference_analysis: Dict[str, Any] = {}

        try:
            pipeline_result = await run_in_threadpool(
                run_validation_pipeline,
                input_path,
                output_path,
                required_sections or None,
                enabled_check_types,
                safe_start_page,
                job_id,
                original_filename,
            )
            errors = pipeline_result.errors
            summary = pipeline_result.summary
            statistics = pipeline_result.statistics
            extracted_data = pipeline_result.extracted_data
            reference_analysis = pipeline_result.reference_analysis
            pipeline_success = pipeline_result.success
        except Exception as proc_exc:
            pipeline_success = False
            pipeline_error_message = str(proc_exc)
            logger.error("[PROCESSING] job_id=%s logic failure: %s", job_id, proc_exc)
            logger.error(traceback.format_exc())

            errors = []
            summary = ValidationSummary(errors=0, pages_with_errors=0, figures=0, tables=0)
            statistics = {
                "pipeline_status": {
                    "current_layer": {
                        "success": False,
                        "message": f"Pipeline failed: {pipeline_error_message}",
                    }
                },
                "partial_result": True,
            }
            extracted_data = {
                "full_text": "",
                "page_texts": [],
                "line_count": 0,
                "pipeline_status": statistics.get("pipeline_status", {}),
            }
            reference_analysis = {
                "error": "Processing pipeline failed before full extraction",
                "detail": pipeline_error_message,
            }

            if not os.path.exists(output_path):
                await run_in_threadpool(shutil.copyfile, input_path, output_path)

        logger.info(
            "[PROCESSING] job_id=%s complete success=%s error_count=%s",
            job_id,
            pipeline_success,
            len(errors),
        )

        json_path = os.path.join(PROCESSED_FOLDER, f"{job_id}_extracted_data.json")

        def _write_extracted_json() -> None:
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(extracted_data, jf, indent=2, ensure_ascii=False)

        await run_in_threadpool(_write_extracted_json)

        processing_results[job_id] = {
            "job_id": job_id,
            "original_filename": original_filename,
            "output_filename": output_filename,
            "input_path": input_path,
            "output_path": output_path,
            "start_page": safe_start_page,
            "summary": summary.model_dump(),
            "errors": [e.model_dump() for e in errors],
            "error_count": summary.errors,
            "statistics": statistics,
            "reference_analysis": reference_analysis,
            "mandatory_sections": required_sections,
            "document_overview": _build_document_overview(
                extracted_data, original_filename, statistics, summary.errors
            ),
            "pipeline_success": pipeline_success,
            "pipeline_error": pipeline_error_message,
            "processed_at": datetime.now().isoformat(),
        }

        return UploadResponse(
            job_id=job_id,
            original_filename=original_filename,
            output_filename=output_filename,
            summary=summary,
            error_count=summary.errors,
            errors=errors,
            statistics=statistics,
            reference_analysis=reference_analysis,
            mandatory_sections=required_sections,
            document_overview=processing_results[job_id]["document_overview"],
            start_page=safe_start_page,
            success=pipeline_success,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[UPLOAD] ERROR: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}") from e


@router.get(
    "/download/{job_id}",
    responses={404: {"model": ErrorResponse}},
)
async def download_file(job_id: str) -> FileResponse:
    result = processing_results.get(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    if not os.path.exists(result["output_path"]):
        raise HTTPException(status_code=404, detail="Processed file not found")
    return FileResponse(
        path=result["output_path"],
        media_type="application/pdf",
        filename=result["output_filename"],
    )


@router.get(
    "/results/{job_id}",
    response_model=JobResult,
    responses={404: {"model": ErrorResponse}},
)
async def get_results(job_id: str) -> JobResult:
    result = processing_results.get(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResult(**result)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="healthy")


@router.get("/debug/sys-check")
async def sys_check() -> Dict[str, Any]:
    metadata = {}
    
    # Check binaries
    for cmd in ["gs", "pdftocairo", "python", "pip"]:
        try:
            res = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            metadata[cmd] = res.stdout.strip() or res.stderr.strip()
        except Exception:
            metadata[cmd] = "MISSING"

    # Check libs
    lib_status = {}
    for lib in ["fitz", "camelot", "cv2", "onnxruntime", "pix2text"]:
        try:
            __import__(lib)
            lib_status[lib] = "OK"
        except ImportError as e:
            lib_status[lib] = f"ERROR: {str(e)}"
        except Exception as e:
            lib_status[lib] = f"CRASH: {str(e)}"
            
    return {
        "binaries": metadata,
        "libraries": lib_status,
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "env": {k: v for k, v in os.environ.items() if "URL" not in k and "KEY" not in k}, # Redact secrets
    }


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    print("Starting Research Paper Error Checker...")
    print("Open your browser to: http://localhost:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
