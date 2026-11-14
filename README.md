# Smart Exam Scheduler

## Introduction

Smart Exam Scheduler is a TH Augsburg project for planning final exams. It checks timetable conflicts and room constraints, generates schedule proposals, and lets administrators review and confirm a version.

## Local setup

Install Python 3.12+, Node.js 22, Docker Compose, and Make. From the repository root:

```bash
python3 -m venv .venv
make install
test -f backend/.env || cp backend/.env.example backend/.env
```

Set your allowed sign-in email and a random `AUTH_SECRET` in `backend/.env`. The example `DATABASE_URL` matches the local PostgreSQL service.

```bash
docker compose -f postgres.compose.yml up -d
.venv/bin/alembic -c backend/alembic.ini upgrade head
make dev
```

## Usage

- [Web app](http://localhost:5173)
- [API documentation](http://localhost:8000/docs)
- [Mailpit](http://localhost:8025) for local sign-in codes

In the API docs, select a planning cycle, validate its current schedule, and generate a proposal. An administrator can confirm the proposal after review.

## Data model

| Area | Models |
| --- | --- |
| Study plans and exams | `StudyPlan` stores the programme code and curriculum version. Each plan has its own `ExamDefinition` records. |
| Examiners | `Examiner` and `ExamDefinitionExaminer` link examiners to exam definitions. |
| Shared exams | `MappingGroup` and `MappingMember` link equivalent exam definitions across study plans. |
| Rooms | `Room` stores room type and capacity. |

The first Alembic migration creates these seven reference tables. The scheduling demo currently reads in-memory data. The planned model groups shared exams into one `ExamEvent` per exam code within a `PlanningCycle`. Each `Schedule` version records its placements as `ExamSitting` records.

See [DEV_DOC.md](DEV_DOC.md) for more on the API and planning workflow.