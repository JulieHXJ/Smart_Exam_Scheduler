from fastapi import FastAPI
from app.api.router import router

# define
app = FastAPI(
    title="Smart Exam Scheduler API",
    description="Backend API for the THA Smart Exam Scheduler project.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Smart Exam Scheduler API"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

@app.get("/info")
def project_info():
    return {
        "project": "Smart Exam Scheduler",
        "faculty": "Faculty of Computer Science",
        "version": "0.1.0",
        "status": "development"
    }

app.include_router(router, prefix="/api")