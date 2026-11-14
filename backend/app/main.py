from dotenv import load_dotenv

load_dotenv()

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.router import router

app = FastAPI(
    title="Smart Exam Scheduler API",
    description="Backend API for the THA Smart Exam Scheduler project.",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/info")
def project_info():
    return {
        "project": "Smart Exam Scheduler",
        "faculty": "Faculty of Computer Science",
        "version": "0.1.0",
        "status": "development",
    }

app.include_router(router, prefix="/api")

def _frontend_dir() -> Path | None:
    if hasattr(sys, "_MEIPASS"):  # packaged by PyInstaller
        path = Path(sys._MEIPASS) / "frontend_dist"
    else:  # repo checkout: <repo>/frontend/dist
        path = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    return path if (path / "index.html").is_file() else None

# Must stay last: the catch-all route would otherwise shadow later routes.
_dist = _frontend_dir()
if _dist:
    app.mount("/assets", StaticFiles(directory=_dist / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = (_dist / full_path).resolve()
        if candidate.is_file() and candidate.is_relative_to(_dist.resolve()):
            return FileResponse(candidate)
        return FileResponse(_dist / "index.html")  # React Router handles the path