"""PDF annotation and response transformation helpers."""
from __future__ import annotations

from typing import Iterable, List

import fitz

from backend.pdf_processor import ErrorInstance
from backend.validation_models import BoundingBox, ValidationIssue


def _issue_to_error_instance(issue: ValidationIssue) -> ErrorInstance:
    bbox = issue.bbox.as_tuple() if issue.bbox else (0.0, 0.0, 200.0, 20.0)
    return ErrorInstance(
        check_id=issue.check_id,
        check_name=issue.check_name,
        description=issue.message,
        page_num=max(0, issue.page - 1),
        text=issue.text or issue.message,
        bbox=bbox,
        error_type=issue.code,
    )


def to_legacy_error_instances(issues: Iterable[ValidationIssue]) -> List[ErrorInstance]:
    return [_issue_to_error_instance(issue) for issue in issues]


def annotate_pdf(pdf_path: str, output_path: str, issues: Iterable[ValidationIssue]) -> None:
    doc = fitz.open(pdf_path)
    color_map = {
        "missing_required_section": (1.00, 0.65, 0.65),
        "invalid_figure_label": (0.95, 0.85, 1.00),
        "figure_numbering_sequence": (0.95, 0.80, 0.95),
        "invalid_table_numbering": (0.80, 0.95, 0.85),
        "table_numbering_sequence": (0.80, 0.95, 0.90),
        "equation_numbering": (1.00, 0.90, 0.70),
    }

    for issue in issues:
        if not issue.bbox:
            continue
        page_index = max(0, issue.page - 1)
        if page_index >= len(doc):
            continue
        page = doc[page_index]
        annot = page.add_highlight_annot(issue.bbox.as_tuple())
        annot.set_colors(stroke=color_map.get(issue.code, (1.00, 1.00, 0.60)))
        annot.set_opacity(0.5)
        annot.info["title"] = f"Check #{issue.check_id}: {issue.check_name}"
        annot.info["content"] = f"{issue.message}\n\nFound: '{issue.text or issue.message}'"
        annot.update()

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
