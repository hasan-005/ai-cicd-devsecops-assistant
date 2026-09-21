from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="AI CI/CD DevSecOps Assistant",
    description="AI-powered CI/CD failure prediction, security and performance analysis",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "project": "AI CI/CD DevSecOps Assistant",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/overview")
def overview():
    return {
        "project_name": "AI CI/CD DevSecOps Assistant",
        "build_status": "Not analyzed",
        "failure_probability": 0,
        "security_score": 100,
        "time_complexity": "Not analyzed",
        "space_complexity": "Not analyzed",
        "build_time": 0,
        "peak_memory": 0,
        "cpu_usage": 0
    }

@app.post("/api/pipelines", response_model=schemas.PipelineRunResponse)
def create_pipeline(
    pipeline: schemas.PipelineRunCreate,
    db: Session = Depends(get_db)
):
    new_pipeline = models.PipelineRun(
        pipeline_id=pipeline.pipeline_id,
        status=pipeline.status,
        build_time=pipeline.build_time,
        tests_passed=pipeline.tests_passed,
        tests_failed=pipeline.tests_failed,
        cpu_usage=pipeline.cpu_usage,
        memory_usage=pipeline.memory_usage,
        vulnerabilities=pipeline.vulnerabilities
    )

    db.add(new_pipeline)
    db.commit()
    db.refresh(new_pipeline)

    return new_pipeline

@app.get("/api/pipelines", response_model=list[schemas.PipelineRunResponse])
def get_pipelines(db: Session = Depends(get_db)):
    pipelines = db.query(models.PipelineRun).all()

    return pipelines


@app.get("/api/pipelines/{pipeline_id}", response_model=schemas.PipelineRunResponse)
def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    pipeline = (
        db.query(models.PipelineRun)
        .filter(models.PipelineRun.pipeline_id == pipeline_id)
        .first()
    )

    if pipeline is None:
        raise HTTPException(
            status_code=404,
            detail="Pipeline not found"
        )

    return pipeline