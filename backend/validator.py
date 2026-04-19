"""Validation rules for structured academic paper documents."""
from __future__ import annotations

import re
from typing import Iterable, List, Optional, Sequence, Set

from backend.detector import FIGURE_LABEL_RE, TABLE_LABEL_RE, build_structured_sections, detect_structured_equations, detect_structured_figures, detect_structured_tables, normalize_section_key, _normalize_text
from backend.validation_models import BoundingBox, ElementCandidate, ParsedDocument, StructuredDocument, StructuredElement, ValidationIssue, ValidationResult, ValidationSummary

FIGURE_SEQUENCE_TYPE = "figure_numbering_sequence"
TABLE_SEQUENCE_TYPE = "table_numbering_sequence"
EQUATION_TYPE = "equation_numbering"
SECTION_TYPE = "missing_required_section"


def _issue(
    *,
    code: str,
    check_id: int,
    check_name: str,
    message: str,
    issue_type: str,
    severity: str,
    page: int,
    bbox: Optional[BoundingBox] = None,
    text: str = "",
    element: Optional[str] = None,
) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        check_id=check_id,
        check_name=check_name,
        message=message,
        type=issue_type,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        page=max(1, page),
        bbox=bbox,
        text=text,
        element=element,
    )


def build_document(parsed: ParsedDocument) -> StructuredDocument:
    sections = build_structured_sections(parsed.lines)
    figures = [
        StructuredElement.model_validate(candidate.model_dump())
        for candidate in detect_structured_figures(
            StructuredDocument(raw_text=parsed.raw_text, lines=parsed.lines), parsed.element_candidates
        )
    ]
    tables = [StructuredElement.model_validate(candidate.model_dump()) for candidate in detect_structured_tables(parsed.element_candidates)]
    equations = [StructuredElement.model_validate(candidate.model_dump()) for candidate in detect_structured_equations(parsed.element_candidates)]

    return StructuredDocument(
        sections=sections,
        figures=figures,
        tables=tables,
        equations=equations,
        raw_text=parsed.raw_text,
        page_texts=parsed.page_texts,
        lines=parsed.lines,
        metadata=parsed.metadata,
        references=parsed.references,
        statistics=parsed.statistics,
        reference_analysis=parsed.reference_analysis,
        page_count=parsed.page_count,
    )


def _pages_with_errors(issues: Iterable[ValidationIssue]) -> int:
    return len({issue.page for issue in issues if issue.page > 0})


def _validate_sections(document: StructuredDocument, required_sections: Optional[Sequence[str]]) -> List[ValidationIssue]:
    """Validate required sections with robust IEEE format matching."""
    issues: List[ValidationIssue] = []
    
    if not document.sections:
        # If NO sections found at all, report all required sections as missing
        required = list(required_sections or ["abstract", "introduction", "references"])
        required_normalized = [sec.lower() for sec in required]
        
        for req_section in required_normalized:
            anchor_page = 1
            issues.append(
                _issue(
                    code=SECTION_TYPE,
                    check_id=27,
                    check_name=f"Missing Required Section: {req_section.title()}",
                    message=f"The required section '{req_section.title()}' was not found.",
                    issue_type="structure",
                    severity="error",
                    page=anchor_page,
                    text=f"[Section '{req_section.title()}' not found]",
                    element="section",
                )
            )
        return issues
    
    # Build normalized lookup of found sections
    found_sections: Set[str] = set()
    for section_key in document.sections.keys():
        # Try direct match
        found_sections.add(section_key)
        # Try normalized match
        section_normalized = normalize_section_key(section_key)
        if section_normalized:
            found_sections.add(section_normalized)
    
    # Required sections for IEEE format papers
    required = list(required_sections or ["abstract", "introduction", "references"])
    required_normalized = [sec.lower() for sec in required]
    
    # Check each required section
    for req_section in required_normalized:
        if req_section in found_sections:
            continue
        
        # Check if we can find it by normalizing the requirement
        found = False
        for found_key in document.sections.keys():
            if normalize_section_key(found_key) == req_section or found_key.lower() == req_section:
                found = True
                break
        
        if found:
            continue
        
        # Not found - report error
        anchor_page = 1
        issues.append(
            _issue(
                code=SECTION_TYPE,
                check_id=27,
                check_name=f"Missing Required Section: {req_section.title()}",
                message=f"The required section '{req_section.title()}' was not found.",
                issue_type="structure",
                severity="error",
                page=anchor_page,
                text=f"[Section '{req_section.title()}' not found]",
                element="section",
            )
        )
    
    return issues


def _validate_figures(document: StructuredDocument) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if not document.figures:
        return issues

    numbers: List[int] = []
    seen = set()
    for figure in document.figures:
        match = FIGURE_LABEL_RE.search(figure.label) or FIGURE_LABEL_RE.search(figure.text)
        if not match:
            issues.append(
                _issue(
                    code="invalid_figure_label",
                    check_id=6,
                    check_name="Figure Label Format",
                    message="Figure labels must use 'Fig. N' or 'Figure N'.",
                    issue_type="formatting",
                    severity="warning",
                    page=figure.page,
                    bbox=figure.bbox,
                    text=figure.label or figure.text,
                    element="figure",
                )
            )
            continue

        number = int(match.group(1))
        numbers.append(number)
        if number in seen:
            continue
        seen.add(number)

    sorted_numbers = sorted(seen)
    for expected, number in enumerate(sorted_numbers, start=1):
        if number != expected:
            offending = next(fig for fig in document.figures if fig.number == number or FIGURE_LABEL_RE.search(fig.label or fig.text))
            issues.append(
                _issue(
                    code=FIGURE_SEQUENCE_TYPE,
                    check_id=21,
                    check_name="Figure Numbering Sequence",
                    message=f"Figure {number} found but expected Figure {expected}.",
                    issue_type="formatting",
                    severity="error",
                    page=offending.page,
                    bbox=offending.bbox,
                    text=offending.label or offending.text,
                    element="figure",
                )
            )

    return issues


def _validate_tables(document: StructuredDocument) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if not document.tables:
        return issues

    numbers: List[int] = []
    seen = set()
    for table in document.tables:
        match = TABLE_LABEL_RE.search(table.label) or TABLE_LABEL_RE.search(table.text)
        if not match:
            issues.append(
                _issue(
                    code="invalid_table_numbering",
                    check_id=7,
                    check_name="Table Label Format",
                    message="Table labels must use 'TABLE I', 'TABLE II', etc.",
                    issue_type="formatting",
                    severity="warning",
                    page=table.page,
                    bbox=table.bbox,
                    text=table.label or table.text,
                    element="table",
                )
            )
            continue

        raw = match.group(1).upper()
        roman_map = {
            "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
            "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20,
        }
        number = roman_map.get(raw)
        if number is None:
            try:
                number = int(raw)
            except ValueError:
                continue
        numbers.append(number)
        if number in seen:
            continue
        seen.add(number)

    sorted_numbers = sorted(seen)
    for expected, number in enumerate(sorted_numbers, start=1):
        if number != expected:
            offending = next(table for table in document.tables if table.number == number or TABLE_LABEL_RE.search(table.label or table.text))
            issues.append(
                _issue(
                    code=TABLE_SEQUENCE_TYPE,
                    check_id=22,
                    check_name="Table Numbering Sequence",
                    message=f"Table {number} found but expected Table {expected}.",
                    issue_type="formatting",
                    severity="error",
                    page=offending.page,
                    bbox=offending.bbox,
                    text=offending.label or offending.text,
                    element="table",
                )
            )

    return issues


def _validate_equations(document: StructuredDocument) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if not document.equations:
        return issues

    numbers: List[int] = []
    seen = set()
    for equation in document.equations:
        if equation.number is None:
            issues.append(
                _issue(
                    code=EQUATION_TYPE,
                    check_id=8,
                    check_name="Equation Numbering",
                    message="Display equations must be numbered as (1), (2), etc.",
                    issue_type="formatting",
                    severity="warning",
                    page=equation.page,
                    bbox=equation.bbox,
                    text=equation.text,
                    element="equation",
                )
            )
            continue
        numbers.append(equation.number)
        if equation.number in seen:
            continue
        seen.add(equation.number)

    sorted_numbers = sorted(seen)
    for expected, number in enumerate(sorted_numbers, start=1):
        if number != expected:
            offending = next(eq for eq in document.equations if eq.number == number)
            issues.append(
                _issue(
                    code=EQUATION_TYPE,
                    check_id=8,
                    check_name="Equation Numbering",
                    message=f"Equation ({number}) found but expected ({expected}).",
                    issue_type="formatting",
                    severity="error",
                    page=offending.page,
                    bbox=offending.bbox,
                    text=offending.text,
                    element="equation",
                )
            )

    return issues


def validate_document(
    parsed: ParsedDocument,
    required_sections: Optional[Sequence[str]] = None,
) -> ValidationResult:
    document = build_document(parsed)
    issues: List[ValidationIssue] = []
    issues.extend(_validate_sections(document, required_sections))
    issues.extend(_validate_figures(document))
    issues.extend(_validate_tables(document))
    issues.extend(_validate_equations(document))

    summary = ValidationSummary(
        errors=len(issues),
        pages_with_errors=_pages_with_errors(issues),
        figures=len(document.figures),
        tables=len(document.tables),
    )
    return ValidationResult(summary=summary, errors=issues, document=document)
