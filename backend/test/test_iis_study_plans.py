from pathlib import Path

import pytest

from app.imports import study_plan_pdf as parser
from app.imports.study_plan import StudyPlanInput, validate_references
from app.imports.study_plan_pdf import SourceRow, classify, parse_study_plan, select_elective_rows, table_rows


def test_subpoint_coordinates_stay_in_one_row():
    rectangles = [
        {"x0": x, "top": 56.601, "bottom": bottom}
        for x, bottom in [(67.894, 115.29500000000002), (167.107, 115.29499999999996)]
    ]
    rows = list(table_rows(rectangles))
    assert len(rows) == 1
    assert len(rows[0]) == 2


def test_iis2021_database_bzv_matches_german_note_and_bilingual_title(monkeypatch):
    exam = SourceRow(
        2, 2, "Datenbanksysteme (Database Systems)", "9770050", "", "",
        "Schriftliche Prüfung (Klausur)\n90 Minuten, keine Hilfsmittel\n"
        "Alternativ zur Klausur können auch 3 Studienarbeiten abgegeben werden.",
        "", "Zulassungsvoraussetzung: Praktikum Datenbanksysteme, vgl. SPO",
    )
    bzv = SourceRow(
        2, 2, "Praktikum Datenbanksysteme\n(Database Systems)", "9770051", "", "",
        "Praktikum", "mit Erfolg/ohne Erfolg", "",
    )
    metadata = {"kind": "compulsory", "spo_version": "2021",
                "source_file": "test.pdf", "source_term": "Wintersemester 2026/2027"}
    monkeypatch.setattr(parser, "read_pdf", lambda _: (metadata, [exam, bzv]))
    document = StudyPlanInput.model_validate(parse_study_plan(Path("test.pdf"), "2021"))
    assert validate_references(document) == []
    assert document.exams[0].duration_minutes == 90
    assert document.prerequisites[0].prerequisite_number == "9770051"


@pytest.mark.parametrize("spo,number", [("2021", "9775212"), ("2024", "9875350")])
def test_elective_spo_comes_from_legend_not_cell_order(monkeypatch, spo, number):
    row = SourceRow(2, None, "Example", "9775212, 9875350", "", "",
                    "Written examination, 60 minutes", "", "")
    metadata = {"kind": "elective", "source_file": "test.pdf",
                "source_term": "winter semester 2026/2027",
                "prefixes": {"2024": "9875", "2021": "9775"}}
    monkeypatch.setattr(parser, "read_pdf", lambda _: (metadata, [row]))
    doc = StudyPlanInput.model_validate(parse_study_plan(Path("test.pdf"), spo))
    assert doc.spo_version == spo
    assert doc.exams[0].exam_number == number
    assert doc.exams[0].is_mandatory is False
    assert doc.exams[0].recommended_semester is None


def test_elective_number_for_other_spo_is_retained_for_review(monkeypatch):
    row = SourceRow(2, None, "Old elective", "9775133", "", "",
                    "Written examination, 60 minutes", "", "")
    metadata = {"kind": "elective", "source_file": "test.pdf",
                "source_term": "winter semester 2026/2027",
                "prefixes": {"2024": "9875", "2021": "9775"}}
    monkeypatch.setattr(parser, "read_pdf", lambda _: (metadata, [row]))
    payload = parse_study_plan(Path("test.pdf"), "2024")
    assert payload["exams"] == []
    assert payload["review"][0]["source_numbers"] == "9775133"


@pytest.mark.parametrize("cell", ["9875350 9875430", "3981712", "9875XXX"])
def test_ambiguous_or_unknown_elective_numbers_are_errors(cell):
    row = SourceRow(1, None, "Example", cell, "", "", "Written examination, 60 minutes", "", "")
    with pytest.raises(ValueError):
        select_elective_rows([row], {"prefixes": {"2024": "9875", "2021": "9775"}}, "2024")


def test_unlisted_spo_is_rejected():
    with pytest.raises(ValueError, match="not in the elective PDF legend"):
        select_elective_rows([], {"prefixes": {"2021": "9775"}}, "2025")


def test_portfolio_written_component_is_not_silently_scheduled():
    row = SourceRow(1, None, "3D printing", "9875260", "", "",
                    "Portfolio exam: Written examination, 60 minutes, 25 %", "", "")
    assert classify(row, "2024", False, mandatory=False)[0] == "review"


def test_german_electronic_exam():
    row = SourceRow(1, 1, "Programmieren 1", "9770030", "", "",
                    "Schriftliche Prüfung, 60 Minuten, durchgeführt als elektronische Prüfung", "", "")
    status, _, exam = classify(row, "2021", False)
    assert status == "exam"
    assert exam["exam_type"] == "digital"
