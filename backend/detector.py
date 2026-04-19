"""Strict detection helpers for structured PDF validation."""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from backend.validation_models import ElementCandidate, ExtractionLine, SectionBlock, StructuredDocument

# Strict patterns for IEEE format academic papers
FIGURE_LABEL_RE = re.compile(r"\b(?:Fig\.?|Figure)\s*(\d+)\b", re.IGNORECASE)
TABLE_LABEL_RE = re.compile(r"\bTABLE\s+([IVXLCDM]+|\d+)\b", re.IGNORECASE)
EQUATION_NUMBER_RE = re.compile(r"\(\s*(\d+)\s*\)\s*$")

# IEEE-format section patterns with text normalization
SECTION_PATTERNS: Dict[str, re.Pattern] = {
    "abstract": re.compile(r"\babstract\b", re.IGNORECASE),
    "introduction": re.compile(r"\b(?:i\.?\s+)?introduction\b", re.IGNORECASE),
    "references": re.compile(r"\breferences?\b", re.IGNORECASE),
    "index_terms": re.compile(r"\b(?:index\s+terms?|keywords?)\b", re.IGNORECASE),
}

# Math operators for equation detection (strict filter - exclude bare parentheses)
# Must contain at least one mathematical operator to be considered an equation
MATH_OPERATORS = r"[=+\-*/^≤≥≈≠∑∫∂∇√]"
MATH_SYMBOLS = r"[α-ωΑ-Ω∀∃∈∉⊂⊃∅∞∂∇]"


def _as_int(page: Optional[int]) -> int:
    try:
        return int(page or 1)
    except Exception:
        return 1


def _normalize_text(text: str) -> str:
    """Normalize text for section matching: remove special dashes, collapse spaces, lowercase."""
    if not text:
        return ""
    # Replace special dashes with space
    text = re.sub(r"[–—−]", " ", text)
    # Remove leading numbers with dots (1., 2., etc.)
    text = re.sub(r"^\s*\d+\.\s*", "", text.strip())
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    # Return normalized lowercase
    return text.strip().lower()


def _roman_to_int(value: str) -> Optional[int]:
    numerals = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6,
        "VII": 7,
        "VIII": 8,
        "IX": 9,
        "X": 10,
        "XI": 11,
        "XII": 12,
        "XIII": 13,
        "XIV": 14,
        "XV": 15,
        "XVI": 16,
        "XVII": 17,
        "XVIII": 18,
        "XIX": 19,
        "XX": 20,
    }
    return numerals.get(value.upper())


def normalize_section_key(text: str) -> Optional[str]:
    """Match section name against IEEE patterns, with text normalization."""
    normalized = _normalize_text(text)
    for key, pattern in SECTION_PATTERNS.items():
        if pattern.search(normalized):
            return key
    return None


def detect_structured_figures(document: StructuredDocument, candidates: List[ElementCandidate]) -> List[ElementCandidate]:
    """Detect figures with strict pattern matching to avoid false positives."""
    figures: List[ElementCandidate] = []
    seen = set()

    for candidate in candidates:
        if candidate.kind != "figure":
            continue
        
        # STRICT: Must have "Fig" or "Figure" label, not just a number
        label = candidate.label.strip()
        text = candidate.text.strip()
        
        # Only match if label or text contains "Fig." or "Figure"
        match = FIGURE_LABEL_RE.search(label) or FIGURE_LABEL_RE.search(text)
        if not match:
            continue
        
        # Extract number from group(1) and deduplicate
        try:
            number = int(match.group(1))
        except (ValueError, IndexError):
            continue
            
        if number in seen:
            continue
        
        seen.add(number)
        figures.append(candidate.model_copy(update={"number": number, "label": label or f"Figure {number}"}))

    return figures


def detect_structured_tables(candidates: List[ElementCandidate]) -> List[ElementCandidate]:
    tables: List[ElementCandidate] = []
    seen = set()

    for candidate in candidates:
        if candidate.kind != "table":
            continue
        label = candidate.label.strip()
        match = TABLE_LABEL_RE.search(label) or TABLE_LABEL_RE.search(candidate.text)
        if not match:
            continue

        raw = match.group(1).upper()
        number = _roman_to_int(raw)
        if number is None:
            try:
                number = int(raw)
            except ValueError:
                continue

        if number in seen:
            continue
        seen.add(number)
        tables.append(candidate.model_copy(update={"number": number, "label": label or f"TABLE {raw}"}))

    return tables


def detect_structured_equations(candidates: List[ElementCandidate]) -> List[ElementCandidate]:
    """Detect ONLY numbered equations with mathematical content."""
    equations: List[ElementCandidate] = []
    seen = set()

    for candidate in candidates:
        if candidate.kind != "equation":
            continue
        
        text = candidate.text.strip()
        
        # STRICT: Must have (N) pattern at end
        match = EQUATION_NUMBER_RE.search(text)
        if not match:
            continue
        
        try:
            number = int(match.group(1))
        except (ValueError, IndexError):
            continue
        
        # STRICT: Must contain math operators or symbols (filter out bullet points, random text)
        has_math_op = re.search(MATH_OPERATORS, text) is not None
        has_math_sym = re.search(MATH_SYMBOLS, text) is not None
        
        if not (has_math_op or has_math_sym):
            continue
        
        # Deduplicate by number
        if number in seen:
            continue
        
        seen.add(number)
        equations.append(candidate.model_copy(update={"number": number}))

    return equations


def build_structured_sections(lines: List[ExtractionLine]) -> Dict[str, SectionBlock]:
    sections: Dict[str, SectionBlock] = {}
    current_key: Optional[str] = None
    current_lines: List[str] = []
    current_page = 1
    current_bbox = None

    def flush() -> None:
        nonlocal current_key, current_lines, current_page, current_bbox
        if current_key:
            sections[current_key] = SectionBlock(
                heading=current_key.replace("_", " ").title(),
                page=current_page,
                bbox=current_bbox,
                content="\n".join(current_lines).strip(),
            )
        current_lines = []

    for line in lines:
        key = normalize_section_key(line.text)
        if key:
            flush()
            current_key = key
            current_page = line.page
            current_bbox = line.bbox
            continue

        if current_key:
            current_lines.append(line.text)

    flush()
    return sections
