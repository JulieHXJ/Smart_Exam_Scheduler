# PrüfPlan Backend Update

19 November 2026

## Milestone

Completed the database foundation, core reference-data models and the first validated study-plan import workflow. Added BZV prerequisite relationships and verified parsing, validation, transactional writes and repeat imports against the supplied IIS study plans.

## Database foundation and models

Established PostgreSQL persistence with SQLAlchemy models, database sessions and Alembic migrations.

| Model | Purpose |
|---|---|
| StudyPlan | Identifies a programme and its SPO version. |
| ExamDefinition | Stores the reusable final-exam number, title, type, duration, recommended semester and compulsory/elective status. |
| Examiner | Stores examiner identities. |
| ExamDefinitionExaminer | Associates exam definitions with examiners. |
| MappingGroup / MappingMember | Represents relationships between equivalent exam definitions. |
| Room | Stores room type and capacity. |
| ExamPrerequisite | Links a final-exam definition to its required Practice/BZV record. |

Migration 0001 creates the initial reference-data tables. Migration 0002 adds exam_prerequisites.

A StudyPlan is identified by programme code and SPO version. An ExamDefinition is identified by its study plan and examination number. These keys keep records from different SPO versions separate and support repeat imports.

## Study-plan parsing and import

Implemented the import workflow under app/imports/.

| Module | Responsibility |
|---|---|
| study_plan_pdf.py | Reads PDF tables, recognises the supported IIS layouts and extracts exams, prerequisites and source information. |
| study_plan.py | Validates extracted data, previews database changes and performs transactional imports. |

Database entities reside in app/db/. Pydantic data structures use app/schemas/.

The parser supports the supplied IIS SPO 2021 and SPO 2024 compulsory-module plans and both language versions of the IIS elective catalogue.

For elective catalogues, the selected SPO and the document's examination-number legend determine which number belongs to each imported exam. Elective records use is_mandatory=false and retain an empty recommended semester where the source provides none.

The preview includes importable records, items requiring review, excluded items and specific validation errors. Source pages and assessment descriptions remain available in the preview for checking against the original PDF.

## Practice/BZV prerequisites

Added ExamPrerequisite with a link to ExamDefinition, the prerequisite examination number and its title. The relationship expresses that the BZV must be passed before the student can take the associated final exam.

| IIS SPO | Database Systems final | Required BZV |
|---|---|---|
| 2021 | 9770050 | 9770051 |
| 2024 | 9872030 | 9872040 |

Database Systems is represented as a 90-minute written final exam. Its Practice/BZV is retained as a prerequisite relationship. Student eligibility feedback and additions to the final-exam participant list belong to the subsequent registration-data integration.

## Validation and database behaviour

Validation checks programme and SPO consistency, required fields, field types and lengths, positive durations, supported examination types, duplicate examination numbers, duplicate prerequisite links and missing target exams.

Unresolved prerequisite references produce an error with the source page and examination number. Invalid input stops before database writes.

| Mode | Behaviour |
|---|---|
| Default | Validates the file and previews extracted records without a database connection. |
| --database | Compares validated records with the database and previews new, updated and unchanged records. |
| --apply | Writes validated records in one transaction and reports the resulting changes. |

Repeated imports match existing records through their keys. Changed fields update the existing record. A failed transaction rolls back the batch.

## Testing and acceptance results

All 45 backend tests passed in the development environment.

Acceptance covered four real PDF files and six file/SPO combinations.

| Source | Selected SPO | Importable exams | BZV links | Review | Excluded |
|---|---|---:|---:|---:|---:|
| IIS compulsory plan, German | 2021 | 17 | 5 | 9 | 3 |
| IIS compulsory plan, English | 2024 | 17 | 5 | 10 | 4 |
| IIS elective catalogue, German | 2021 | 21 | 0 | 44 | 0 |
| IIS elective catalogue, German | 2024 | 18 | 0 | 47 | 0 |
| IIS elective catalogue, English | 2021 | 21 | 0 | 44 | 0 |
| IIS elective catalogue, English | 2024 | 18 | 0 | 47 | 0 |

Verified file parsing, validation, read-only database preview, initial writes and repeat imports using SQLite. Tests also covered SPO isolation, record updates, rollback on a simulated write failure and interactive command-line input.

After importing both compulsory plans and the elective catalogues for both SPO versions, the acceptance database contained 2 study plans, 73 exam definitions and 10 prerequisite links. Re-importing the same source produced zero new or updated records.

The German and English elective catalogues share examination numbers. Importing the other language updates translated titles in existing records. Selecting a preferred language source keeps display titles consistent.

The local PostgreSQL service was started and reported that it was accepting connections. PostgreSQL migration, import and direct-query acceptance commands are documented in docs/iis-study-plan-demo.md. The automated database results above were obtained with SQLite.

## Review items and continuation

Portfolio assessments, missing examination numbers and ambiguous scheduling scope remain visible for review. Some source-language versions also contain differing assessment details, which require confirmation before those records are added to the final-exam schedule.

The next integration step is to connect imported reference data to the planning workflow, followed by registration imports, BZV eligibility feedback and updates to the final-exam participant list.
