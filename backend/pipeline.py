"""Orchestrates parsing, detection, validation, and reporting."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Sequence, Set

from backend.detector import detect_structured_equations, detect_structured_figures, detect_structured_tables
from backend.parser import parse_pdf
from backend.reporting import annotate_pdf
from backend.validation_models import ParsedDocument, PipelineResult, StructuredDocument, ValidationIssue
from backend.validator import validate_document


def _filter_issues(issues: List[ValidationIssue], enabled_check_types: Optional[Set[str]]) -> List[ValidationIssue]:
    if enabled_check_types is None:
        return issues
    return [issue for issue in issues if issue.code in enabled_check_types]


def run_validation_pipeline(
    pdf_path: str,
    output_path: Optional[str] = None,
    required_sections: Optional[Sequence[str]] = None,
    enabled_check_types: Optional[Set[str]] = None,
    start_page: int = 1,
    job_id: str = "",
    original_filename: str = "",
) -> PipelineResult:
    parsed = parse_pdf(pdf_path, start_page=start_page)
    validation = validate_document(parsed, required_sections=required_sections)
    issues = _filter_issues(validation.errors, enabled_check_types)

    summary = validation.summary.model_copy(update={"errors": len(issues)})
    document = validation.document.model_copy(
        update={
            "figures": detect_structured_figures(validation.document, validation.document.figures),
            "tables": detect_structured_tables(validation.document.tables),
            "equations": detect_structured_equations(validation.document.equations),
        }
    )

    if output_path:
        annotate_pdf(pdf_path, output_path, issues)

    extracted_data = {
        "full_text": parsed.raw_text,
        "total_characters": len(parsed.raw_text),
        "page_texts": parsed.page_texts,
        "total_pages": parsed.page_count,
        "line_count": len(parsed.lines),
        "lines": [line.model_dump() for line in parsed.lines],
        "sections": {key: value.model_dump() for key, value in document.sections.items()},
        "figures": [figure.model_dump() for figure in document.figures],
        "tables": [table.model_dump() for table in document.tables],
        "equations": [equation.model_dump() for equation in document.equations],
        "metadata": parsed.metadata,
        "reference_analysis": parsed.reference_analysis,
        "statistics": parsed.statistics,
    }

    return PipelineResult(
        job_id=job_id,
        original_filename=original_filename,
        input_path=pdf_path,
        output_path=output_path or pdf_path,
        success=True,
        summary=summary,
        errors=issues,
        document=document,
        extracted_data=extracted_data,
        statistics=parsed.statistics,
        reference_analysis=parsed.reference_analysis,
        mandatory_sections=list(required_sections or []),
        processed_at=datetime.now().isoformat(),
    )
