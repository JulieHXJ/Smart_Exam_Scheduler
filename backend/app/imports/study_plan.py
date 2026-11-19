"""Validate, preview and import a study plan and its final exams and BZVs."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import ExamDefinition, ExamPrerequisite, ProgramCode, StudyPlan
from app.db.session import database_engine


Identifier = Annotated[str, Field(min_length=1, max_length=64)]
ExamNumber = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[0-9]+$")]
Title = Annotated[str, Field(min_length=1, max_length=255)]
PositiveInt = Annotated[int, Field(strict=True, gt=0, le=2_147_483_647)]


class ImportRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("*", mode="before")
    @classmethod
    def reject_nul(cls, value):
        if isinstance(value, str) and "\x00" in value:
            raise ValueError("NUL characters are not allowed")
        return value


class ExamInput(ImportRecord):
    exam_number: ExamNumber
    title: Title
    duration_minutes: PositiveInt
    exam_type: Literal["written", "digital"]
    recommended_semester: PositiveInt | None = None
    is_mandatory: bool = Field(strict=True)
    page: PositiveInt | None = None
    description: str = ""
    note: str = ""


class PrerequisiteInput(ImportRecord):
    exam_number: ExamNumber
    prerequisite_number: ExamNumber
    title: Title
    page: PositiveInt | None = None


class StudyPlanInput(ImportRecord):
    program_code: ProgramCode
    spo_version: Identifier
    source_file: str
    source_term: str | None = None
    exams: list[ExamInput]
    prerequisites: list[PrerequisiteInput] = Field(default_factory=list)
    review: list[dict] = Field(default_factory=list)
    excluded: list[dict] = Field(default_factory=list)


def validate_references(document: StudyPlanInput) -> list[str]:
    errors = []
    exam_numbers: set[str] = set()
    for index, exam in enumerate(document.exams):
        if exam.exam_number in exam_numbers:
            errors.append(f"exams[{index}].exam_number: duplicate {exam.exam_number!r}")
        exam_numbers.add(exam.exam_number)
    pairs: set[tuple[str, str]] = set()
    for index, prerequisite in enumerate(document.prerequisites):
        location = f"prerequisites[{index}]"
        if prerequisite.exam_number not in exam_numbers:
            errors.append(f"{location}.exam_number: no exam {prerequisite.exam_number!r} in this document")
        pair = prerequisite.exam_number, prerequisite.prerequisite_number
        if pair in pairs:
            errors.append(f"{location}: duplicate BZV link {pair!r}")
        if prerequisite.prerequisite_number in exam_numbers:
            errors.append(f"{location}: BZV number is also a scheduled exam number")
        pairs.add(pair)
    if not document.exams:
        errors.append("exams: no importable final exams")
    return errors


def load_document(path: Path, spo_version: str | None = None) -> StudyPlanInput:
    if not path.is_file():
        raise ValueError(f"source file not found: {path}")
    if path.suffix.lower() == ".pdf":
        from app.imports.study_plan_pdf import parse_study_plan
        payload = parse_study_plan(path, spo_version=spo_version)
    elif path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(payload, dict) and "document" in payload and "status" in payload:
            payload = payload["document"]
    else:
        raise ValueError(f"unsupported source extension {path.suffix!r}: {path}; expected .pdf or .json")
    return StudyPlanInput.model_validate(payload)


EXAM_FIELDS = (
    "exam_number", "title", "duration_minutes", "exam_type",
    "recommended_semester", "is_mandatory",
)


def import_document(session: Session, document: StudyPlanInput, *, apply: bool) -> dict:
    """Caller owns the transaction; preview executes SELECTs only."""
    if apply and session.bind.dialect.name == "postgresql":
        # Covers both concurrent creation and concurrent updates of the same plan.
        digest = hashlib.sha256(
            f"{document.program_code.value}\0{document.spo_version}".encode()
        ).digest()
        lock_key = int.from_bytes(digest[:8], "big", signed=True)
        session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})

    plan = session.scalar(select(StudyPlan).filter_by(
        program_code=document.program_code, spo_version=document.spo_version,
    ))
    plan_action = "new" if plan is None else "unchanged"
    definitions = {}
    existing_prerequisites = {}
    if plan is not None:
        definitions = {
            exam.exam_number: exam for exam in session.scalars(
                select(ExamDefinition).filter_by(study_plan_id=plan.id)
            )
        }
        existing_prerequisites = {
            (item.exam_definition_id, item.prerequisite_number): item
            for item in session.scalars(
                select(ExamPrerequisite).join(ExamDefinition)
                .where(ExamDefinition.study_plan_id == plan.id)
            )
        }
    elif apply:
        plan = StudyPlan(program_code=document.program_code, spo_version=document.spo_version)
        session.add(plan)
        session.flush()

    changes = []
    for exam in document.exams:
        values = exam.model_dump(include=set(EXAM_FIELDS))
        current = definitions.get(exam.exam_number)
        action = "new"
        if current is not None:
            action = "updated" if any(
                getattr(current, name) != value for name, value in values.items()
            ) else "unchanged"
        changes.append({"table": "exam_definitions", "number": exam.exam_number, "action": action})
        if apply:
            if current is None:
                current = ExamDefinition(study_plan=plan, **values)
                session.add(current)
                definitions[exam.exam_number] = current
            else:
                for name, value in values.items():
                    setattr(current, name, value)
    if apply:
        session.flush()

    for prerequisite in document.prerequisites:
        exam = definitions.get(prerequisite.exam_number)
        current = None
        if exam is not None:
            current = existing_prerequisites.get((exam.id, prerequisite.prerequisite_number))
        action = "new"
        if current is not None:
            action = "unchanged" if current.title == prerequisite.title else "updated"
        changes.append({
            "table": "exam_prerequisites", "exam_number": prerequisite.exam_number,
            "number": prerequisite.prerequisite_number, "action": action,
        })
        if apply:
            if current is None:
                session.add(ExamPrerequisite(
                    exam_definition=exam,
                    prerequisite_number=prerequisite.prerequisite_number,
                    title=prerequisite.title,
                ))
            else:
                current.title = prerequisite.title

    counts = {}
    for table in ("exam_definitions", "exam_prerequisites"):
        counter = Counter(change["action"] for change in changes if change["table"] == table)
        counts[table] = {action: counter[action] for action in ("new", "updated", "unchanged")}
    return {"study_plan": plan_action, "counts": counts, "changes": changes}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", help="PDF or JSON path; prompted when omitted")
    parser.add_argument("--program-code", choices=[code.value for code in ProgramCode])
    parser.add_argument("--spo-version", help="actual SPO version, not enrolment year")
    parser.add_argument("--database", action="store_true", help="preview changes against the migrated database")
    parser.add_argument("--apply", action="store_true", help="commit validated exams and BZV links")

    args = parser.parse_args(argv)
    if args.source is not None and not args.source.strip():
        parser.error("source path is empty. Check the shell variable or run without arguments for prompts.")

    prompts = (
        ("source", "PDF/JSON file path"),
        ("program_code", "Program code (IIS/WI/IN/TI/KIR/WPF/ITPM/SE)"),
        ("spo_version", "SPO version (from the PDF heading)"),
    )
    for name, question in prompts:
        if getattr(args, name) is None:
            if not sys.stdin.isatty():
                parser.error(f"missing {name}; pass it as an argument or run in an interactive terminal")
            print(f"{question}: ", file=sys.stderr, end="", flush=True)
            try:
                answer = input().strip()
            except (EOFError, KeyboardInterrupt):
                parser.error("input cancelled")
            if not answer:
                parser.error(f"{name} must not be empty")
            setattr(args, name, answer)

    if args.program_code not in {code.value for code in ProgramCode}:
        parser.error("unknown program code")
    source = args.source.strip()
    if len(source) >= 2 and source[0] == source[-1] and source[0] in ("'", '"'):
        source = source[1:-1]
    try:
        document = load_document(Path(source).expanduser(), spo_version=args.spo_version.strip())
    except ValidationError as exc:
        errors = [
            f"{'.'.join(map(str, error['loc']))}: {error['msg']}" for error in exc.errors()
        ]
        print(json.dumps({"status": "invalid", "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1

    errors = validate_references(document)
    if document.program_code.value != args.program_code:
        errors.append(f"program_code: source is {document.program_code.value}, requested {args.program_code}")
    if document.spo_version != args.spo_version.strip():
        errors.append(f"spo_version: source is {document.spo_version}, requested {args.spo_version}")
    report = {
        "status": "invalid" if errors else "validated",
        "errors": errors,
        "summary": {
            "exams": len(document.exams), "prerequisites": len(document.prerequisites),
            "review": len(document.review), "excluded": len(document.excluded),
        },
        "document": document.model_dump(mode="json"),
    }
    if errors:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    if args.database or args.apply:
        try:
            with Session(database_engine()) as session, session.begin():
                result = import_document(session, document, apply=args.apply)
        except (SQLAlchemyError, RuntimeError):
            report["status"] = "database_error"
            report["errors"] = [
                "Database operation failed. Check DATABASE_URL and run Alembic upgrade head. "
                "The import transaction has been rolled back."
            ]
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 1
        report["database"] = result
        report["status"] = "applied" if args.apply else "preview"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
