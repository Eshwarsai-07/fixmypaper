"""Pydantic models for the structured PDF validation pipeline."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x0, self.y0, self.x1, self.y1)


class ExtractionLine(BaseModel):
    text: str
    page: int
    bbox: BoundingBox


class SectionBlock(BaseModel):
    heading: str
    page: int
    bbox: Optional[BoundingBox] = None
    content: str = ""


class ElementCandidate(BaseModel):
    kind: Literal["figure", "table", "equation"]
    label: str = ""
    number: Optional[int] = None
    page: int
    bbox: Optional[BoundingBox] = None
    text: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParsedDocument(BaseModel):
    raw_text: str = ""
    page_texts: List[str] = Field(default_factory=list)
    lines: List[ExtractionLine] = Field(default_factory=list)
    section_heads: List[SectionBlock] = Field(default_factory=list)
    element_candidates: List[ElementCandidate] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    references: List[Dict[str, Any]] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    reference_analysis: Dict[str, Any] = Field(default_factory=dict)
    page_count: int = 0


class StructuredElement(BaseModel):
    kind: Literal["figure", "table", "equation"]
    label: str = ""
    number: Optional[int] = None
    page: int
    bbox: Optional[BoundingBox] = None
    text: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StructuredDocument(BaseModel):
    sections: Dict[str, SectionBlock] = Field(default_factory=dict)
    figures: List[StructuredElement] = Field(default_factory=list)
    tables: List[StructuredElement] = Field(default_factory=list)
    equations: List[StructuredElement] = Field(default_factory=list)
    raw_text: str = ""
    page_texts: List[str] = Field(default_factory=list)
    lines: List[ExtractionLine] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    references: List[Dict[str, Any]] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    reference_analysis: Dict[str, Any] = Field(default_factory=dict)
    page_count: int = 0


class ValidationIssue(BaseModel):
    code: str
    check_id: int
    check_name: str
    message: str
    type: Literal["formatting", "structure"]
    severity: Literal["warning", "error"]
    page: int
    text: str = ""
    bbox: Optional[BoundingBox] = None
    element: Optional[str] = None


class ValidationSummary(BaseModel):
    errors: int
    pages_with_errors: int
    figures: int
    tables: int


class ValidationResult(BaseModel):
    summary: ValidationSummary
    errors: List[ValidationIssue] = Field(default_factory=list)
    document: StructuredDocument


class PipelineResult(BaseModel):
    job_id: str = ""
    original_filename: str = ""
    input_path: str = ""
    output_path: str = ""
    success: bool = True
    summary: ValidationSummary
    errors: List[ValidationIssue] = Field(default_factory=list)
    document: StructuredDocument
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    reference_analysis: Dict[str, Any] = Field(default_factory=dict)
    mandatory_sections: List[str] = Field(default_factory=list)
    processed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
