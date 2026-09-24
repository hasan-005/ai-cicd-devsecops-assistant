import os
import tempfile
from pathlib import Path

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File
)
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db
from .performance import measure_performance
from .complexity import analyze_complexity
from .security import analyze_trivy_report

from samples.sample_code import calculate_sum


# Create database tables
models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI CI/CD DevSecOps Assistant",
    description="AI-powered CI/CD failure prediction, security and performance analysis",
    version="1.0.0"
)


# --------------------------------------------------
# BASIC ROUTES
# --------------------------------------------------

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


# --------------------------------------------------
# PIPELINE ROUTES
# --------------------------------------------------

@app.post(
    "/api/pipelines",
    response_model=schemas.PipelineRunResponse
)
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


@app.get(
    "/api/pipelines",
    response_model=list[schemas.PipelineRunResponse]
)
def get_pipelines(
    db: Session = Depends(get_db)
):
    pipelines = db.query(
        models.PipelineRun
    ).all()

    return pipelines


@app.get(
    "/api/pipelines/{pipeline_id}",
    response_model=schemas.PipelineRunResponse
)
def get_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db)
):
    pipeline = (
        db.query(models.PipelineRun)
        .filter(
            models.PipelineRun.pipeline_id == pipeline_id
        )
        .first()
    )

    if pipeline is None:
        raise HTTPException(
            status_code=404,
            detail="Pipeline not found"
        )

    return pipeline


# --------------------------------------------------
# PERFORMANCE ANALYSIS
# --------------------------------------------------

@app.get("/api/performance/test")
def performance_test():
    metrics = measure_performance(
        calculate_sum
    )

    return {
        "file": "sample_code.py",
        "function": "calculate_sum",
        "performance": metrics
    }


# --------------------------------------------------
# COMPLEXITY ANALYSIS
# --------------------------------------------------

@app.get("/api/complexity/test")
def complexity_test():
    file_path = Path(
        "samples/sample_code.py"
    )

    result = analyze_complexity(
        file_path
    )

    return {
        "file": "sample_code.py",
        "complexity": result
    }


@app.get("/api/complexity/nested")
def complexity_nested():
    file_path = Path(
        "samples/nested_loop.py"
    )

    result = analyze_complexity(
        file_path
    )

    return {
        "file": "nested_loop.py",
        "complexity": result
    }


# --------------------------------------------------
# COMBINED SAMPLE ANALYSIS
# --------------------------------------------------

@app.get("/api/analyze/sample")
def analyze_sample():
    file_path = Path(
        "samples/sample_code.py"
    )

    complexity_result = (
        analyze_complexity(file_path)
    )

    performance_result = (
        measure_performance(
            calculate_sum
        )
    )

    return {
        "file": "sample_code.py",
        "complexity_analysis":
            complexity_result,
        "performance_analysis":
            performance_result
    }


# --------------------------------------------------
# UPLOAD PYTHON FILE FOR COMPLEXITY ANALYSIS
# --------------------------------------------------

@app.post("/api/analyze/upload")
async def analyze_uploaded_file(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".py"):
        raise HTTPException(
            status_code=400,
            detail="Only Python (.py) files are allowed"
        )

    contents = await file.read()

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".py"
        ) as temp_file:

            temp_file.write(contents)
            temp_path = temp_file.name

        complexity_result = (
            analyze_complexity(
                temp_path
            )
        )

        return {
            "file": file.filename,
            "complexity_analysis":
                complexity_result
        }

    finally:
        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)


# --------------------------------------------------
# SECURITY ANALYSIS
# --------------------------------------------------

@app.post("/api/security/analyze")
async def analyze_security_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.lower().endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="Only JSON files are allowed"
        )

    contents = await file.read()

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".json"
        ) as temp_file:

            temp_file.write(contents)
            temp_path = temp_file.name

        # Analyze Trivy report
        result = analyze_trivy_report(
            temp_path
        )

        # Save security scan to database
        new_scan = models.SecurityScan(
            critical=result["critical"],
            high=result["high"],
            medium=result["medium"],
            low=result["low"],
            vulnerabilities=result[
                "vulnerabilities"
            ],
            secrets=result["secrets"],
            misconfigurations=result[
                "misconfigurations"
            ],
            security_score=result[
                "security_score"
            ],
            risk_level=result[
                "risk_level"
            ]
        )

        db.add(new_scan)
        db.commit()
        db.refresh(new_scan)

        return {
            "scan_id": new_scan.id,
            "file": file.filename,
            "security_analysis":
                result,
            "saved_to_database":
                True
        }

    finally:
        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)

@app.get("/api/security/history")
def get_security_history(
    db: Session = Depends(get_db)
):
    scans = (
        db.query(models.SecurityScan)
        .order_by(models.SecurityScan.id.desc())
        .all()
    )

    return [
        {
            "id": scan.id,
            "critical": scan.critical,
            "high": scan.high,
            "medium": scan.medium,
            "low": scan.low,
            "vulnerabilities": scan.vulnerabilities,
            "secrets": scan.secrets,
            "misconfigurations": scan.misconfigurations,
            "security_score": scan.security_score,
            "risk_level": scan.risk_level,
            "created_at": scan.created_at
        }
        for scan in scans
    ]

@app.get("/api/security/latest")
def get_latest_security_scan(
    db: Session = Depends(get_db)
):
    scan = (
        db.query(models.SecurityScan)
        .order_by(models.SecurityScan.id.desc())
        .first()
    )

    if scan is None:
        raise HTTPException(
            status_code=404,
            detail="No security scans found"
        )

    return {
        "id": scan.id,
        "critical": scan.critical,
        "high": scan.high,
        "medium": scan.medium,
        "low": scan.low,
        "vulnerabilities": scan.vulnerabilities,
        "secrets": scan.secrets,
        "misconfigurations": scan.misconfigurations,
        "security_score": scan.security_score,
        "risk_level": scan.risk_level,
        "created_at": scan.created_at
    }

@app.get("/api/security/deployment-check")
def deployment_security_check(
    db: Session = Depends(get_db)
):
    scan = (
        db.query(models.SecurityScan)
        .order_by(models.SecurityScan.id.desc())
        .first()
    )

    if scan is None:
        raise HTTPException(
            status_code=404,
            detail="No security scan available"
        )

    # Deployment rule:
    # Any critical vulnerability blocks deployment.
    if scan.critical > 0:
        return {
            "deployment_allowed": False,
            "reason": "Deployment blocked because critical vulnerabilities were detected.",
            "security_score": scan.security_score,
            "risk_level": scan.risk_level,
            "critical": scan.critical,
            "high": scan.high
        }

    return {
        "deployment_allowed": True,
        "reason": "No critical vulnerabilities detected.",
        "security_score": scan.security_score,
        "risk_level": scan.risk_level,
        "critical": scan.critical,
        "high": scan.high
    }