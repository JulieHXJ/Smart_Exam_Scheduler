# Smart Exam Scheduler — Developer Documentation

**Status:** Planning workflow and email OTP backend implemented as development MVP; frontend integration and production hardening pending. 
**Updated:** Nov 2026

## 1. Architectural goal

Smart Exam Scheduler is a **change-aware, iterative examination planning application**. A Planning Cycle retains its identity while data and constraints evolve. Administrators can validate an existing schedule, generate a candidate revision, inspect its differences, and confirm a new version without overwriting historical versions.

### Unified workflow

```text
Open / Create Planning Cycle
            |
Load reusable reference data and current examinations
            |
    Update data (optional) 
            |                                    
   Detect changes / review impact                
            |                                   
  Review or edit constraint configuration <------+ 
            |                                    |
    Validate current schedule                    |
            |                                    |
      Generate proposal                          |
            |                                    |
       Review and compare -----------------------+
            |
     Confirm & save version
            |
       Export (optional)
```

Registration data is provided in second stage; absence of registration data must not block an initial schedule. 

## 2. Repository organization

The current backend is organized around FastAPI routers, Pydantic models, mock data, and validation functions. The following tree is the **target organization for the ongoing prototype**; files that are not yet on remote `main` must be created or committed from the local feature branch.

```text
backend/
  app/
    main.py
    api/
      router.py
      auth.py
      planning_cycle.py
      rooms.py
      proposals.py
    auth/core.py
    data/mock_data.py
    data/demo_plan.py
    validator/schedule.py
    generator/proposal.py
    generator/schedule_diff.py
    models/...
  test/
    test_auth_api.py
    test_proposal_api.py
    test_room_api.py
    test_schedule_validation.py
  .env.example
  requirements.txt
frontend/
  src/features/auth/components/LoginForm.tsx
  src/pages/LoginPage.tsx
  src/app/router.tsx
  vite.config.ts
mailpit.compose.yml
DEV_DOC.md
```



## 3. Domain model and ownership

| Concept | Purpose | Lifetime |
| --- | --- | --- |
| StudyPlan | Curriculum and program-specific examination references | Cross-cycle reference data |
| ExamDefinition | Reusable examination identity and basic properties | Cross-cycle reference data |
| PlanningCycle | One semester's exam-planning period | One planning period |
| ExamEvent | An examination demand for a specific cycle | One Planning Cycle |
| Registration | A student's registration for an examination occurrence | Specific cycle/occurrence |
| ExamSitting | A concrete sitting or batch of an ExamEvent | Subject to final scheduling design |
| Schedule | One planned or confirmed version | Versioned per cycle |


## 4. Validation architecture

Current schedule validation implementation:

```text
validate_schedule(...)
  ├── check_exam_exists(...)
  ├── check_exam_period(...)
  ├── check_room_exists(...)
  ├── check_room_capacity(...)
  ├── check_room_availability(...)
  └── check_room_overlap(...)
```


**Implemented/tested categories:**

- Examination outside the allowed planning period.
- Insufficient combined room capacity.
- Room unavailable during an examination.
- Overlapping examination assignments using the same room.


## 6. API design

### Authentication endpoints

| Method | Endpoint | Behavior |
| --- | --- | --- |
| POST | `/api/auth/request-code` | JSON `{ "email": "..." }`; generic response regardless of whether allowlisted |
| POST | `/api/auth/verify-code` | JSON `{ "email": "...", "code": "..." }`; validates and sets session cookie |
| GET | `/api/auth/me` | Current authenticated email and role |
| POST | `/api/auth/logout` | Invalidate and clear session cookie |


### Planning endpoints

| Method | Endpoint | Behavior |
| --- | --- | --- |
| GET | `/api/exams` | Mock examinations |
| GET | `/api/rooms` | Mock rooms |
| GET | `/api/students` | Mock students |
| GET | `/api/registrations` | Mock registrations |
| GET | `/api/planning-cycles` | List cycles |
| GET | `/api/planning-cycles/{cycle_id}` | Read cycle |
| GET | `/api/planning-cycles/{cycle_id}/schedules/current` | Current confirmed schedule |
| PUT | `/api/rooms/{room_id}/unavailability` | Add/update blocked interval |
| POST | `/api/planning-cycles/{cycle_id}/validate` | Validate current schedule |
| POST | `/api/planning-cycles/{cycle_id}/proposals` | Generate proposal |
| GET | `/api/proposals/{proposal_id}` | Proposal and diff |
| POST | `/api/proposals/{proposal_id}/confirm` | Confirm new version |



## 7. Local development

Follow the [local setup for your platform](README.md#local-setup). Start the full development stack with `make dev` on macOS or Linux, or `.\dev.ps1` from Windows PowerShell.

For local email testing, configure the allowed sign-in email, `AUTH_SECRET`, and the Mailpit SMTP settings in `backend/.env`. The example sets SMTP port `1025`. Restart FastAPI after changing the file.

- [Mailpit UI](http://localhost:8025)
- [Swagger](http://localhost:8000/docs)

End-to-end local check: request OTP → read in Mailpit → verify OTP → /api/auth/me returns the role → logout → /api/auth/me returns 401. Placeholder email addresses are valid only when Mailpit intercepts local messages.

### Database setup and migrations

From the repository root, start PostgreSQL and check that it is ready:

```text
docker compose -f postgres.compose.yml up -d
docker compose -f postgres.compose.yml exec db pg_isready -U smart_exam -d smart_exam
```

The example `DATABASE_URL` in `backend/.env.example` matches the local Compose service. Confirm that `backend/.env` has the corresponding value, then apply migrations:

- macOS or Linux: `make migrate`
- Windows PowerShell: `.\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini upgrade head`

## 9. Next milestones

1. React OTP integration (frontend owner): connect the four endpoints, remove password form, create protected routes.
2. Backend authorization: admin-only proposal confirmation; decide tester permissions for every mutation; add negative tests.
3. End-to-end integration: Mailpit, browser OTP, session persistence within one server run, logout, invalid/expired code/error UX.
4. PostgreSQL: persist PlanningCycle, Schedule, room unavailability, proposals, OTP/session state; include migrations and safe updates.
5. Planning Workspace: load cycle/schedule, visualize diffs, review constraints, generate/confirm proposals.
6. Data pipeline: import reference data and later real registrations; reconcile exam events per cycle.
7. Solver: expand hard/soft constraints, benchmark against greedy baseline, evaluate constraint solving / optimization.
8. Delivery and AI: deployment/security review, audit trail/export, then AI-assisted analysis when deterministic rules are stable.

