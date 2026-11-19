from pathlib import Path
from types import SimpleNamespace

import pytest

from app.imports import study_plan_pdf as pdf_parser
from app.imports.study_plan import StudyPlanInput, validate_references
from app.imports.study_plan_pdf import SourceRow, classify, parse_study_plan, read_pdf


def source_row(number="9872030", description="Written examination, 90 minutes", note=""):
    return SourceRow(4, 3, "Database Systems", number, "First", "Second", description, "", note)


def test_database_final_rule_is_scoped_to_verified_number_and_spo():
    row = source_row(description="Written examination, 90 minutes\nAlternative Portfolio exam:")
    status, _, exam = classify(row, "2024", False)
    assert status == "exam"
    assert exam["duration_minutes"] == 90
    assert exam["exam_type"] == "written"
    assert classify(row, "2025", False)[0] == "review"
    assert classify(source_row(number="9872029", description=row.description), "2024", False)[0] == "review"


def test_bzv_link_uses_note_and_exact_source_title(monkeypatch):
    exam = source_row(note="Requirements for participation: Practical work Database Systems, cf. SPO")
    practice = SourceRow(4, 3, "Practical work\nDatabase Systems", "9872040", "", "", "Practical work", "", "")
    metadata = {"spo_version": "2024", "source_file": "test.pdf", "source_term": "winter semester 2026/2027"}
    monkeypatch.setattr(pdf_parser, "read_pdf", lambda _: (metadata, [exam, practice]))
    document = StudyPlanInput.model_validate(parse_study_plan(Path("test.pdf")))
    assert validate_references(document) == []
    assert document.prerequisites[0].exam_number == "9872030"
    assert document.prerequisites[0].prerequisite_number == "9872040"

    monkeypatch.setattr(pdf_parser, "read_pdf", lambda _: (metadata, [exam]))
    with pytest.raises(ValueError, match="expected one numbered BZV"):
        parse_study_plan(Path("test.pdf"))


@pytest.mark.parametrize("number,description", [
    ("9871XXX", "Written examination, 60 minutes"),
    ("9875251", "Oral examination, 15-30 minutes"),
    ("9872020", "Portfolio exam: Written examination, 60 minutes"),
])
def test_ambiguous_assessments_stay_in_review(number, description):
    assert classify(source_row(number, description), "2024", False)[0] == "review"


def test_unknown_pdf_layout_is_rejected(monkeypatch):
    page = SimpleNamespace(extract_text=lambda **_: "Unrecognised programme", rects=[])
    class PDF:
        pages = [page]
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    monkeypatch.setattr(pdf_parser.pdfplumber, "open", lambda _: PDF())
    with pytest.raises(ValueError, match="unsupported PDF heading"):
        read_pdf(Path("unknown.pdf"))
