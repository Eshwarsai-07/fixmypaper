"""PDF parsing layer that extracts structured candidates from a document."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

import fitz

from backend.detector import EQUATION_NUMBER_RE, FIGURE_LABEL_RE, TABLE_LABEL_RE, _as_int
from backend.pdf_processor import PDFErrorDetector
from backend.validation_models import BoundingBox, ElementCandidate, ExtractionLine, ParsedDocument, SectionBlock


def _bbox_from_tuple(value: Any) -> BoundingBox:
    x0, y0, x1, y1 = value
    return BoundingBox(x0=float(x0), y0=float(y0), x1=float(x1), y1=float(y1))


def _extract_caption_label(text: str, pattern: re.Pattern) -> str:
    match = pattern.search(text)
    return match.group(0).strip() if match else ""


class PDFParser:
    """Adapter around the existing extraction stack."""

    def parse(self, pdf_path: str, start_page: int = 1) -> ParsedDocument:
        detector = PDFErrorDetector(start_page=start_page)
        doc = fitz.open(pdf_path)

        detector._extract_with_grobid(pdf_path)
        detector._extract_all_text(doc)
        detector._extract_tables(pdf_path)

        citations = detector._extract_citations_grobid(pdf_path)
        detector.raw_citations = citations
        detector.reference_analysis = detector.analyze_references(citations)
        statistics = detector._collect_statistics(doc)

        lines = [
            ExtractionLine(text=text, page=_as_int(page_num + 1), bbox=_bbox_from_tuple(bbox))
            for text, bbox, page_num in detector.line_info
        ]

        section_heads = [
            SectionBlock(
                heading=head["text"].strip(),
                page=_as_int(head["page"] + 1),
                bbox=_bbox_from_tuple(head["bbox"]),
            )
            for head in detector._grobid_section_heads
        ]

        figure_candidates: List[ElementCandidate] = []
        for fig in detector._grobid_figure_entries:
            figure_candidates.append(
                ElementCandidate(
                    kind="figure",
                    label=fig.get("label", "").strip() or fig.get("caption", "").strip(),
                    number=fig.get("number"),
                    page=_as_int(fig.get("page", 0) + 1),
                    bbox=_bbox_from_tuple(fig["bbox"]),
                    text=fig.get("caption", "").strip(),
                    metadata={"xml_coords": fig.get("xml_coords", "")},
                )
            )

        table_candidates: List[ElementCandidate] = []
        for table in detector.extracted_tables:
            df = table.get("dataframe")
            rows = df.values.tolist() if df is not None else []
            row_text = "\n".join(" | ".join(str(cell) for cell in row) for row in rows[:5])
            page = _as_int(table.get("page", 1))
            caption = ""
            for line in lines:
                if line.page != page:
                    continue
                if TABLE_LABEL_RE.search(line.text):
                    caption = line.text.strip()
                    break
            label = _extract_caption_label(caption, TABLE_LABEL_RE)
            if not label and len(rows) < 2:
                continue
            table_candidates.append(
                ElementCandidate(
                    kind="table",
                    label=label,
                    page=page,
                    text=caption or row_text,
                    metadata={
                        "rows": len(rows),
                        "columns": len(df.columns) if df is not None else 0,
                        "accuracy": table.get("accuracy"),
                        "whitespace": table.get("whitespace"),
                    },
                )
            )

        equation_candidates: List[ElementCandidate] = []
        # STRICT: Only accept equations from GROBID if they have proper numbering and math content
        for eq in detector._grobid_equations:
            text = eq.get("text", "").strip()
            number = eq.get("number")
            
            # Only accept if numbered
            if number is None:
                continue
            
            # Check for mathematical content (operators or symbols)
            has_math = re.search(r"[=+\-*/^×÷≤≥≈≠∑∫∂∇√]", text)
            if not has_math:
                continue
            
            equation_candidates.append(
                ElementCandidate(
                    kind="equation",
                    label=f"({number})",
                    number=number,
                    page=_as_int(eq.get("page", 0) + 1),
                    bbox=_bbox_from_tuple(eq["bbox"]),
                    text=text,
                    metadata={"source": "grobid"},
                )
            )

        # Fallback: Scan lines for properly numbered equations with math symbols ONLY
        if not equation_candidates:
            for line in lines:
                # Must have (N) pattern at end of line
                if not EQUATION_NUMBER_RE.search(line.text):
                    continue
                
                # STRICT: Must contain math operators (not just any parentheses)
                if not re.search(r"[=+\-*/^×÷≤≥≈≠∑∫∂∇√]", line.text):
                    continue
                
                # Extract number
                match = EQUATION_NUMBER_RE.search(line.text)
                number = int(match.group(1))
                
                equation_candidates.append(
                    ElementCandidate(
                        kind="equation",
                        label=f"({number})",
                        number=number,
                        page=line.page,
                        bbox=line.bbox,
                        text=line.text,
                        metadata={"source": "line_scan"},
                    )
                )

        parsed = ParsedDocument(
            raw_text=detector.full_text,
            page_texts=detector.page_texts,
            lines=lines,
            section_heads=section_heads,
            element_candidates=[*figure_candidates, *table_candidates, *equation_candidates],
            metadata=detector._grobid_metadata,
            references=citations,
            statistics=statistics,
            reference_analysis=detector.reference_analysis,
            page_count=len(doc),
        )

        doc.close()
        return parsed


def parse_pdf(pdf_path: str, start_page: int = 1) -> ParsedDocument:
    return PDFParser().parse(pdf_path, start_page=start_page)
