"""Parse the supplied IIS compulsory and elective study plans (SPO 2021/2024)."""

import re
from collections import Counter
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pdfminer.pdfparser import PDFSyntaxError
from pdfplumber.utils.exceptions import PdfminerException


HEADERS = (
    ("Title", "Exam. number", "First examiner", "Second examiner",
     "Type of examination", "Grading", "Note"),
    ("Fach", "Prüfungs- nummer", "Erstprüfer", "Zweitprüfer",
     "Art", "Benotung", "Anmerkung"),
)
PLAN_TITLE = re.compile(r"International Information Systems \(Bachelor\) SPO ([0-9]{4})", re.I)
ELECTIVE_TITLES = {
    "Required Elective Modules Bachelor International Information Systems",
    "Wahlpflichtfächer Bachelor International Information Systems",
}
TERM = re.compile(
    r"(?:Examinations(?: and study plan)? in|Prüfungen(?: und Studienplan)? im) "
    r"((?:winter|summer) semester \d{4}/\d{4}|(?:Winter|Sommer)semester \d{4}(?:/\d{4})?)",
    re.I,
)
PREFIX = re.compile(r"IIS SPO ([0-9]{4}) (?:with|mit) ([0-9]+)[xX]+")
SEMESTER = re.compile(r"([1-9][0-9]*)(?:(?:st|nd|rd|th) semester|\. Semester)", re.I)
FIXED_EXAM = re.compile(
    r"^(written examination|schriftliche prüfung|elektronische prüfung)"
    r"(?: \((?:written examination|klausur)\))?[, ]+([1-9][0-9]*) (?:minutes?|minuten)\b",
    re.I,
)
OUT_OF_SCOPE = {
    "internship": "internship report",
    "praktische tätigkeit": "internship report",
    "bachelor thesis": "thesis submission",
    "bachelorarbeit": "thesis submission",
    "compulsory elective subjects": "reference to elective catalogue",
    "general science elective subjects": "reference to elective catalogue",
    "fachbezogene wahlpflichtmodule": "reference to elective catalogue",
}


@dataclass(frozen=True)
class SourceRow:
    page: int
    semester: int | None
    title: str
    exam_number: str
    first_examiner: str
    second_examiner: str
    description: str
    grading: str
    note: str
    source_numbers: str = ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def base_title(text: str) -> str:
    """Ignore bilingual translations when matching a BZV against its note."""
    text = re.sub(r"\([^)]*\)", "", normalized(text))
    return re.sub(r"(?<=\w)-\s+(?=\w)", "", normalized(text)).casefold()


def table_rows(rectangles):
    """Group cells with sub-point PDF rounding differences into the same row."""
    cells = []
    for rect in sorted(rectangles, key=lambda item: (item["top"], item["x0"])):
        if cells and (
            abs(rect["top"] - cells[0]["top"]) > 0.05
            or abs(rect["bottom"] - cells[0]["bottom"]) > 0.05
        ):
            yield sorted(cells, key=lambda item: item["x0"])
            cells = []
        cells.append(rect)
    if cells:
        yield sorted(cells, key=lambda item: item["x0"])


def read_pdf(path: Path) -> tuple[dict, list[SourceRow]]:
    rows = []
    semester = None
    columns = None
    with pdfplumber.open(path) as pdf:
        if not pdf.pages:
            raise ValueError("PDF has no pages")
        lines = pdf.pages[0].extract_text(x_tolerance=1).splitlines()
        plan = next(filter(None, map(PLAN_TITLE.fullmatch, lines)), None)
        elective = any(line in ELECTIVE_TITLES for line in lines)
        term = next(filter(None, map(TERM.fullmatch, lines)), None)
        if (not plan and not elective) or not term:
            raise ValueError("unsupported PDF heading; expected an IIS compulsory or elective study plan")
        prefixes = dict(PREFIX.findall(" ".join(lines)))
        if elective and not prefixes:
            raise ValueError("elective PDF: missing SPO-to-exam-number legend")
        metadata = {
            "source_file": path.name, "source_term": term[1],
            "kind": "elective" if elective else "compulsory",
            "spo_version": plan[1] if plan else None, "prefixes": prefixes,
        }
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1)
            if not page.rects and text.startswith("Details of the practical semester"):
                continue
            if not page.rects:
                raise ValueError(f"page {page.page_number}: missing study-plan table")
            for cells in table_rows(page.rects):
                if len(cells) != 7:
                    raise ValueError(f"page {page.page_number}: expected seven cells per table row")
                values = tuple(
                    page.crop((cell["x0"], cell["top"], cell["x1"], cell["bottom"]))
                    .extract_text(x_tolerance=1).strip()
                    for cell in cells
                )
                positions = tuple((round(cell["x0"], 1), round(cell["x1"], 1)) for cell in cells)
                if tuple(normalized(value) for value in values) in HEADERS:
                    columns = positions
                elif (heading := SEMESTER.fullmatch(values[0])) and not any(values[1:]):
                    semester = int(heading[1])
                elif normalized(values[0]) == "Wahlpflichtmodule" and not any(values[1:]):
                    continue
                elif columns == positions and values[0] and values[4] and (elective or semester):
                    rows.append(SourceRow(page.page_number, semester, *values))
                else:
                    raise ValueError(f"page {page.page_number}: unexpected table row near {values[0]!r}")
    if not rows:
        raise ValueError("no study-plan module rows found")
    return metadata, rows


def is_practice(row: SourceRow) -> bool:
    description = normalized(row.description).casefold()
    return description in {"practical work", "praktikum"}


def classify(
    row: SourceRow, spo_version: str, duplicated: bool, mandatory: bool = True,
) -> tuple[str, str, dict | None]:
    title = normalized(row.title)
    description = normalized(row.description).casefold()
    if is_practice(row):
        return "prerequisite", "BZV requirement linked using the final exam note", None
    if reason := OUT_OF_SCOPE.get(base_title(title)):
        return "excluded", reason, None
    if not re.fullmatch(r"[0-9]+", row.exam_number):
        return "review", "official exam number missing or placeholder", None
    if duplicated:
        return "review", "exam number appears more than once in the selected SPO", None
    exam = FIXED_EXAM.match(description)
    database_final = (
        mandatory and (spo_version, row.exam_number) in {("2024", "9872030"), ("2021", "9770050")}
        and "database systems" in title.casefold() and exam is not None and int(exam[2]) == 90
    )
    if any(word in description for word in ("portfolio", "alternativ")) and not database_final:
        return "review", "portfolio or alternative assessment needs scope confirmation", None
    if exam is None:
        return "review", "no supported final written exam with a fixed duration", None
    digital = any(phrase in description for phrase in (
        "elektronische prüfung", "carried out as electronic examination",
    ))
    return "exam", "confirmed final only" if database_final else "final written exam", {
        "exam_number": row.exam_number, "title": title, "duration_minutes": int(exam[2]),
        "exam_type": "digital" if digital else "written",
        "recommended_semester": row.semester, "is_mandatory": mandatory,
        "page": row.page, "description": row.description, "note": row.note,
    }


def select_elective_rows(rows: list[SourceRow], metadata: dict, spo_version: str) -> list[SourceRow]:
    prefixes = metadata["prefixes"]
    if spo_version not in prefixes:
        raise ValueError(f"SPO {spo_version} is not in the elective PDF legend; available: {', '.join(prefixes)}")
    selected = []
    for row in rows:
        numbers = re.findall(r"\b[0-9]{7}\b", row.exam_number)
        residue = re.sub(r"\b[0-9]{7}\b|[\s,;–—-]", "", row.exam_number)
        if residue or any(not any(n.startswith(prefix) for prefix in prefixes.values()) for n in numbers):
            raise ValueError(f"page {row.page}, {row.title!r}: unrecognised exam-number cell {row.exam_number!r}")
        matching = [number for number in numbers if number.startswith(prefixes[spo_version])]
        if len(matching) > 1:
            raise ValueError(f"page {row.page}: multiple exam numbers for SPO {spo_version}: {matching}")
        number = matching[0] if matching else ""
        selected.append(replace(row, exam_number=number, source_numbers=row.exam_number))
    return selected


def parse_study_plan(path: Path, spo_version: str | None = None) -> dict:
    try:
        metadata, rows = read_pdf(path)
    except (PDFPasswordIncorrect, PDFSyntaxError, PdfminerException) as exc:
        raise ValueError(f"cannot read PDF: {exc}") from exc
    mandatory = metadata.get("kind", "compulsory") == "compulsory"
    if mandatory:
        source_spo = metadata["spo_version"]
    else:
        if spo_version is None:
            raise ValueError("select a SPO version when parsing an elective PDF")
        source_spo = spo_version
        rows = select_elective_rows(rows, metadata, source_spo)
    counts = Counter(row.exam_number for row in rows)
    payload = {
        "program_code": "IIS", "spo_version": source_spo,
        "source_file": metadata["source_file"], "source_term": metadata["source_term"],
        "exams": [], "prerequisites": [], "review": [], "excluded": [],
    }
    practice_rows = [row for row in rows if is_practice(row)]
    used_practices = set()
    for row in rows:
        status, reason, exam = classify(row, source_spo, counts[row.exam_number] > 1, mandatory)
        if not mandatory and row.source_numbers and not row.exam_number:
            reason = "no official exam number for the selected SPO"
        if status == "prerequisite":
            continue
        if status != "exam":
            payload[status].append({**asdict(row), "reason": reason})
            continue
        note = normalized(row.note)
        if "Requirements for participation:" in note or "Zulassungsvoraussetzung:" in note:
            reference = re.search(
                r"(?:Requirements for participation:|Zulassungsvoraussetzung:)\s*"
                r"((?:Practical work|Praktikum) .+?),\s*(?:cf\.|vgl\.)\s*SPO",
                note,
            )
            if reference is None:
                raise ValueError(f"page {row.page}, exam {row.exam_number}: cannot resolve prerequisite note")
            matches = [practice for practice in practice_rows if base_title(practice.title) == base_title(reference[1])]
            if len(matches) != 1 or not re.fullmatch(r"[0-9]+", matches[0].exam_number):
                raise ValueError(
                    f"page {row.page}, exam {row.exam_number}: expected one numbered BZV "
                    f"matching {reference[1]!r}, found {len(matches)}"
                )
            practice = matches[0]
            payload["prerequisites"].append({
                "exam_number": row.exam_number, "prerequisite_number": practice.exam_number,
                "title": normalized(practice.title), "page": practice.page,
            })
            used_practices.add(practice)
        payload["exams"].append(exam)
    for row in practice_rows:
        if row not in used_practices:
            payload["review"].append({**asdict(row), "reason": "BZV could not be linked to an importable final exam"})
    return payload
