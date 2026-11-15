# Smart Exam Scheduler

## Introduction

Smart Exam Scheduler is a TH Augsburg project for planning final exams. It checks timetable conflicts and room constraints, generates schedule proposals, and lets administrators review and confirm a version.

## Local setup

Run setup commands from the repository root. Install Python 3.12+, Node.js 22, and Docker with Compose. Start Docker before launching the app.

### macOS or Linux

Install Make, then run:

```bash
python3 -m venv .venv
make install
test -f backend/.env || cp backend/.env.example backend/.env
```

Set your allowlisted sign-in email and a random `AUTH_SECRET` in `backend/.env`. Then run `make dev` to start Mailpit, FastAPI, and Vite.

### Windows (PowerShell)

Run these commands once to set up the Windows virtual environment and install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
npm.cmd --prefix frontend ci
if (-not (Test-Path backend\.env)) {
    Copy-Item backend\.env.example backend\.env
}
```

Set your allowlisted sign-in email and a random `AUTH_SECRET` in `backend\.env`. For daily use, start Docker Desktop and run:

```powershell
.\dev.ps1
```

The script starts Mailpit and opens separate PowerShell windows for FastAPI and Vite. If PowerShell blocks the script, run `powershell -NoProfile -ExecutionPolicy Bypass -File .\dev.ps1` to allow it for that invocation.

### PostgreSQL

For work that uses PostgreSQL, see [database setup and migrations](DEV_DOC.md#database-setup-and-migrations). The scheduling demo uses in-memory data.

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
