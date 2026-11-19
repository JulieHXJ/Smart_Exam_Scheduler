import json
from copy import deepcopy
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.imports import study_plan as importer
from app.db.models import Base, ExamDefinition, ExamPrerequisite, StudyPlan


SAMPLE = Path(__file__).parent / "fixtures/study_plan_iis2024.json"


@pytest.fixture
def db(monkeypatch):
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    monkeypatch.setattr(importer, "database_engine", lambda: engine)
    yield engine
    engine.dispose()


def run(source, capsys, *extra, spo="2024", expected=0):
    result = importer.main([
        str(source), "--program-code", "IIS", "--spo-version", spo, *extra,
    ])
    report = json.loads(capsys.readouterr().out)
    assert result == expected, report
    return report


def write_document(tmp_path, payload):
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_preview_repeat_update_and_older_exam_records(db, tmp_path, capsys):
    with Session(db) as session, session.begin():
        plan = StudyPlan(program_code="IIS", spo_version="2024")
        session.add(ExamDefinition(
            study_plan=plan, exam_number="00001", title="Existing exam",
            duration_minutes=60, exam_type="written", is_mandatory=True,
        ))
    report = run(SAMPLE, capsys, "--database")
    assert report["database"]["counts"]["exam_definitions"]["new"] == 1
    with Session(db) as session:
        assert len(session.scalars(select(ExamDefinition)).all()) == 1

    first = run(SAMPLE, capsys, "--apply")
    assert first["database"]["counts"]["exam_prerequisites"]["new"] == 1
    repeated = run(SAMPLE, capsys, "--apply")
    assert repeated["database"]["counts"] == {
        "exam_definitions": {"new": 0, "updated": 0, "unchanged": 1},
        "exam_prerequisites": {"new": 0, "updated": 0, "unchanged": 1},
    }

    payload = deepcopy(repeated["document"])
    payload["exams"][0]["duration_minutes"] = 120
    payload["prerequisites"][0]["title"] = "Updated BZV title"
    source = write_document(tmp_path, payload)
    assert run(source, capsys, "--database")["database"]["counts"]["exam_definitions"]["updated"] == 1
    with Session(db) as session:
        assert session.scalar(
            select(ExamDefinition.duration_minutes).where(ExamDefinition.exam_number == "9872030")
        ) == 90

    updated = run(source, capsys, "--apply")
    assert updated["database"]["counts"]["exam_prerequisites"]["updated"] == 1
    with Session(db) as session:
        assert len(session.scalars(select(ExamDefinition)).all()) == 2
        assert session.scalars(select(ExamPrerequisite)).one().title == "Updated BZV title"


def test_spo_scope_keeps_numbers_and_bzv_links_separate(db, tmp_path, capsys):
    run(SAMPLE, capsys, "--apply")
    document = json.loads(SAMPLE.read_text())
    document["spo_version"] = "2025"
    # Synthetic version-isolation fixture; this is not a source-derived SPO 2025 mapping.
    source = write_document(tmp_path, document)
    report = run(source, capsys, "--apply", spo="2025")
    assert report["database"]["study_plan"] == "new"
    with Session(db) as session:
        assert len(session.scalars(select(StudyPlan)).all()) == 2
        assert len(session.scalars(select(ExamDefinition)).all()) == 2
        links = session.scalars(select(ExamPrerequisite)).all()
        assert len(links) == 2
        assert links[0].exam_definition_id != links[1].exam_definition_id


@pytest.mark.parametrize("problem", ["spo", "duplicate_exam", "orphan_bzv", "duplicate_bzv", "duration"])
def test_invalid_input_has_specific_errors_and_never_opens_database(tmp_path, capsys, monkeypatch, problem):
    payload = json.loads(SAMPLE.read_text())
    expected_field = "spo_version"
    if problem == "spo":
        payload["spo_version"] = "2025"
    elif problem == "duplicate_exam":
        payload["exams"].append(deepcopy(payload["exams"][0]))
        expected_field = "exams[1].exam_number"
    elif problem == "orphan_bzv":
        payload["prerequisites"][0]["exam_number"] = "99999"
        expected_field = "prerequisites[0].exam_number"
    elif problem == "duplicate_bzv":
        payload["prerequisites"].append(deepcopy(payload["prerequisites"][0]))
        expected_field = "prerequisites[1]"
    else:
        payload["exams"][0]["duration_minutes"] = 0
        expected_field = "exams.0.duration_minutes"

    def unexpected_connection():
        pytest.fail("invalid input must fail before a DB connection")

    monkeypatch.setattr(importer, "database_engine", unexpected_connection)
    report = run(write_document(tmp_path, payload), capsys, "--apply", expected=1)
    assert report["status"] == "invalid"
    assert any(expected_field in error for error in report["errors"])


def test_bzv_write_failure_rolls_back_exams_and_plan(db, capsys):
    with db.begin() as connection:
        connection.exec_driver_sql(
            """CREATE TRIGGER reject_bzv BEFORE INSERT ON exam_prerequisites
            BEGIN SELECT RAISE(ABORT, 'simulated write failure'); END"""
        )
    report = run(SAMPLE, capsys, "--apply", expected=1)
    assert report["status"] == "database_error"
    with Session(db) as session:
        assert session.scalar(select(StudyPlan)) is None
        assert session.scalar(select(ExamDefinition)) is None
        assert session.scalar(select(ExamPrerequisite)) is None


def test_preview_report_is_reusable_as_input(db, tmp_path, capsys):
    report = run(SAMPLE, capsys)
    source = write_document(tmp_path, report)
    assert run(source, capsys, "--apply")["status"] == "applied"


def test_interactive_prompts_keep_json_output_clean(monkeypatch, capsys):
    answers = iter([str(SAMPLE), "IIS", "2024"])
    monkeypatch.setattr(importer.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: next(answers))
    assert importer.main([]) == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["status"] == "validated"
    assert "PDF/JSON file path" in captured.err
    assert "SPO version" in captured.err


def test_empty_shell_variable_has_clear_message(capsys):
    with pytest.raises(SystemExit) as error:
        importer.main(["", "--program-code", "IIS", "--spo-version", "2024"])
    assert error.value.code == 2
    assert "source path is empty" in capsys.readouterr().err


def test_missing_path_has_clear_file_error(tmp_path, capsys):
    report = run(tmp_path / "missing.pdf", capsys, expected=1)
    assert "source file not found" in report["errors"][0]
