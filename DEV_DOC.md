# Smart Exam Scheduler — Developer Documentation

**Status:** Working technical specification and implementation notes   
**Updated:** October 2026

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
├── app/
│   ├── main.py                  # FastAPI app
│   ├── api/
│   │   ├── router.py            
│   │   ├── planning_cycles.py   
│   │   ├── rooms.py             
│   │   └── proposals.py         
│   ├── data/
│   │   ├── mock_data.py         # Static sample exams/rooms/students
│   │   └── demo_plan.py        # In-memory cycle, schedule, room-block state
│   ├── models/
│   │   ├── exam.py
│   │   ├── room.py
│   │   ├── schedule.py
│   │   ├── planning_cycle.py
│   │   └── validator.py
│   ├── validation/
│   │   └── schedule.py          # Independent hard-constraint checks
│   └── services/               # Proposal and diff logic
├── test/
│   ├── test_schedule_validation.py
│   └── test_room_api.py
└── requirements.txt
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


### Prototype endpoints

| Method | Route | Behavior |
| --- | --- | --- |
| GET | `/api/exams` | Return mock examinations |
| GET | `/api/rooms` | Return mock rooms |
| GET | `/api/students` | Return mock students |
| GET | `/api/registrations` | Return mock registrations |
| GET | `/api/planning-cycles` | List cycles |
| GET | `/api/planning-cycles/{cycle_id}` | Get cycle metadata |
| GET | `/api/planning-cycles/{cycle_id}/schedules/current` | Read current confirmed version |
| PUT | `/api/rooms/{room_id}/unavailability` | Add/replace a blocked room interval |
| POST | `/api/planning-cycles/{cycle_id}/validate` | Check the current confirmed schedule |
| POST | `/api/planning-cycles/{cycle_id}/proposals` | Generate a candidate using the current confirmed schedule |
| GET | `/api/proposals/{proposal_id}` | Return proposal and baseline diff |
| POST | `/api/proposals/{proposal_id}/confirm` | Revalidate and save a confirmed new version |



## 7. Local development

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest httpx
python -m uvicorn app.main:app --reload
```

URL: `http://127.0.0.1:8000/docs`.

Run unit tests from `backend/`:

```bash
python -m pytest -v
```

**Reported local baseline:** 9 passing tests as of the room-availability API milestone. The newer proposal services and APIs have not yet been verified as complete.

## 8. Limitations

- All demo data is currently held in memory; it does not survive a restart.
- Data import, automatic ExamEvent reconciliation, and real registration handling are not implemented.
- Student/examiner clashes, soft constraints, special exam equipment, and faculty-specific rules need further work.
- Multi-room and ExamSitting semantics are not finalized.
- The initial generator is intended only as a heuristic demonstration.
- No production-ready authorization, concurrent transaction safety, or audit trail yet.
- PostgreSQL, frontend, and LLM integration are planned.

## 9. Next milestones

1. Implement and test the proposal generator and schedule diff.
2. Add proposal read/confirm endpoints and stale-proposal prevention.
3. Add tests verifying V1 is unchanged and V2 becomes current after confirmation.
4. Build a minimal Vue Planning Workspace connected to the demonstrated API flow.
5. Replace in-memory state with PostgreSQL and migration-backed persistence.
6. Extend data import, ExamDefinition/ExamEvent reconciliation, and real scheduling constraints.
7. Replace the heuristic generator with a constraint-based optimizer and later integrate AI-assisted replanning.

