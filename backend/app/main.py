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

from .database import (
    engine,
    get_db
)

from .performance import (
    measure_performance
)

from .complexity import (
    analyze_complexity
)

from .security import (
    analyze_trivy_report
)

from .predictor import (
    predict_failure
)

from samples.sample_code import (
    calculate_sum
)


# ============================================================
# DATABASE TABLE CREATION
# ============================================================

models.Base.metadata.create_all(
    bind=engine
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI CI/CD DevSecOps Assistant",
    description=(
        "AI-powered CI/CD failure prediction, "
        "security, complexity and performance analysis"
    ),
    version="1.0.0"
)


# ============================================================
# BASIC ROUTES
# ============================================================

@app.get("/")
def home():

    return {
        "project":
            "AI CI/CD DevSecOps Assistant",

        "status":
            "running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.get("/api/overview")
def overview():

    return {
        "project_name":
            "AI CI/CD DevSecOps Assistant",

        "build_status":
            "Not analyzed",

        "failure_probability":
            0,

        "security_score":
            100,

        "time_complexity":
            "Not analyzed",

        "space_complexity":
            "Not analyzed",

        "build_time":
            0,

        "peak_memory":
            0,

        "cpu_usage":
            0
    }


# ============================================================
# PIPELINE ROUTES
# ============================================================

@app.post(
    "/api/pipelines",
    response_model=schemas.PipelineRunResponse
)
def create_pipeline(
    pipeline: schemas.PipelineRunCreate,
    db: Session = Depends(get_db)
):

    new_pipeline = models.PipelineRun(

        pipeline_id=
            pipeline.pipeline_id,

        status=
            pipeline.status,

        build_time=
            pipeline.build_time,

        tests_passed=
            pipeline.tests_passed,

        tests_failed=
            pipeline.tests_failed,

        cpu_usage=
            pipeline.cpu_usage,

        memory_usage=
            pipeline.memory_usage,

        vulnerabilities=
            pipeline.vulnerabilities
    )

    db.add(new_pipeline)

    db.commit()

    db.refresh(new_pipeline)

    return new_pipeline


@app.get(
    "/api/pipelines",
    response_model=
        list[schemas.PipelineRunResponse]
)
def get_pipelines(
    db: Session = Depends(get_db)
):

    pipelines = (
        db.query(models.PipelineRun)
        .order_by(
            models.PipelineRun.id.desc()
        )
        .all()
    )

    return pipelines


@app.get(
    "/api/pipelines/{pipeline_id}",
    response_model=
        schemas.PipelineRunResponse
)
def get_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db)
):

    pipeline = (

        db.query(
            models.PipelineRun
        )

        .filter(
            models.PipelineRun.pipeline_id
            == pipeline_id
        )

        .first()
    )

    if pipeline is None:

        raise HTTPException(
            status_code=404,
            detail="Pipeline not found"
        )

    return pipeline


# ============================================================
# PERFORMANCE ANALYSIS
# ============================================================

@app.get("/api/performance/test")
def performance_test():

    metrics = measure_performance(
        calculate_sum
    )

    return {
        "file":
            "sample_code.py",

        "function":
            "calculate_sum",

        "performance":
            metrics
    }


# ============================================================
# COMPLEXITY ANALYSIS
# ============================================================

@app.get("/api/complexity/test")
def complexity_test():

    file_path = Path(
        "samples/sample_code.py"
    )

    result = analyze_complexity(
        file_path
    )

    return {
        "file":
            "sample_code.py",

        "complexity":
            result
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
        "file":
            "nested_loop.py",

        "complexity":
            result
    }


# ============================================================
# COMBINED SAMPLE ANALYSIS
# ============================================================

@app.get("/api/analyze/sample")
def analyze_sample():

    file_path = Path(
        "samples/sample_code.py"
    )

    complexity_result = (
        analyze_complexity(
            file_path
        )
    )

    performance_result = (
        measure_performance(
            calculate_sum
        )
    )

    return {
        "file":
            "sample_code.py",

        "complexity_analysis":
            complexity_result,

        "performance_analysis":
            performance_result
    }


# ============================================================
# PYTHON FILE UPLOAD + COMPLEXITY ANALYSIS
# ============================================================

@app.post("/api/analyze/upload")
async def analyze_uploaded_file(

    file: UploadFile = File(...),

    db: Session = Depends(get_db)
):

    filename = file.filename or ""

    if not filename.lower().endswith(".py"):

        raise HTTPException(
            status_code=400,
            detail=(
                "Only Python (.py) "
                "files are allowed"
            )
        )

    contents = await file.read()

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".py"
        ) as temp_file:

            temp_file.write(
                contents
            )

            temp_path = (
                temp_file.name
            )

        complexity_result = (
            analyze_complexity(
                temp_path
            )
        )

        new_analysis = (
            models.CodeAnalysis(

                file_name=
                    filename,

                time_complexity=
                    complexity_result[
                        "time_complexity"
                    ],

                space_complexity=
                    complexity_result[
                        "space_complexity"
                    ]
            )
        )

        db.add(
            new_analysis
        )

        db.commit()

        db.refresh(
            new_analysis
        )

        return {

            "analysis_id":
                new_analysis.id,

            "file":
                filename,

            "complexity_analysis":
                complexity_result,

            "saved_to_database":
                True
        }

    finally:

        if (
            temp_path
            and os.path.exists(
                temp_path
            )
        ):

            os.remove(
                temp_path
            )


# ============================================================
# SECURITY ANALYSIS
# ============================================================

@app.post("/api/security/analyze")
async def analyze_security_report(

    file: UploadFile = File(...),

    db: Session = Depends(get_db)
):

    filename = file.filename or ""

    if not filename.lower().endswith(
        ".json"
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JSON files "
                "are allowed"
            )
        )

    contents = await file.read()

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".json"
        ) as temp_file:

            temp_file.write(
                contents
            )

            temp_path = (
                temp_file.name
            )

        result = (
            analyze_trivy_report(
                temp_path
            )
        )

        new_scan = (
            models.SecurityScan(

                critical=
                    result[
                        "critical"
                    ],

                high=
                    result[
                        "high"
                    ],

                medium=
                    result[
                        "medium"
                    ],

                low=
                    result[
                        "low"
                    ],

                vulnerabilities=
                    result[
                        "vulnerabilities"
                    ],

                secrets=
                    result[
                        "secrets"
                    ],

                misconfigurations=
                    result[
                        "misconfigurations"
                    ],

                security_score=
                    result[
                        "security_score"
                    ],

                risk_level=
                    result[
                        "risk_level"
                    ]
            )
        )

        db.add(
            new_scan
        )

        db.commit()

        db.refresh(
            new_scan
        )

        return {

            "scan_id":
                new_scan.id,

            "file":
                filename,

            "security_analysis":
                result,

            "saved_to_database":
                True
        }

    finally:

        if (
            temp_path
            and os.path.exists(
                temp_path
            )
        ):

            os.remove(
                temp_path
            )


# ============================================================
# SECURITY HISTORY
# ============================================================

@app.get("/api/security/history")
def get_security_history(
    db: Session = Depends(get_db)
):

    scans = (

        db.query(
            models.SecurityScan
        )

        .order_by(
            models.SecurityScan.id.desc()
        )

        .all()
    )

    return [

        {
            "id":
                scan.id,

            "critical":
                scan.critical,

            "high":
                scan.high,

            "medium":
                scan.medium,

            "low":
                scan.low,

            "vulnerabilities":
                scan.vulnerabilities,

            "secrets":
                scan.secrets,

            "misconfigurations":
                scan.misconfigurations,

            "security_score":
                scan.security_score,

            "risk_level":
                scan.risk_level,

            "created_at":
                scan.created_at
        }

        for scan in scans
    ]


# ============================================================
# LATEST SECURITY RESULT
# ============================================================

@app.get("/api/security/latest")
def get_latest_security_scan(
    db: Session = Depends(get_db)
):

    scan = (

        db.query(
            models.SecurityScan
        )

        .order_by(
            models.SecurityScan.id.desc()
        )

        .first()
    )

    if scan is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "No security scans found"
            )
        )

    return {

        "id":
            scan.id,

        "critical":
            scan.critical,

        "high":
            scan.high,

        "medium":
            scan.medium,

        "low":
            scan.low,

        "vulnerabilities":
            scan.vulnerabilities,

        "secrets":
            scan.secrets,

        "misconfigurations":
            scan.misconfigurations,

        "security_score":
            scan.security_score,

        "risk_level":
            scan.risk_level,

        "created_at":
            scan.created_at
    }


# ============================================================
# SECURITY DEPLOYMENT CHECK
# ============================================================

@app.get(
    "/api/security/deployment-check"
)
def deployment_security_check(
    db: Session = Depends(get_db)
):

    scan = (

        db.query(
            models.SecurityScan
        )

        .order_by(
            models.SecurityScan.id.desc()
        )

        .first()
    )

    if scan is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "No security scan available"
            )
        )

    if scan.critical > 0:

        return {

            "deployment_allowed":
                False,

            "reason":
                (
                    "Deployment blocked because "
                    "critical vulnerabilities "
                    "were detected."
                ),

            "security_score":
                scan.security_score,

            "risk_level":
                scan.risk_level,

            "critical":
                scan.critical,

            "high":
                scan.high
        }

    return {

        "deployment_allowed":
            True,

        "reason":
            (
                "No critical "
                "vulnerabilities detected."
            ),

        "security_score":
            scan.security_score,

        "risk_level":
            scan.risk_level,

        "critical":
            scan.critical,

        "high":
            scan.high
    }


# ============================================================
# ML FAILURE PREDICTION
# ============================================================

@app.post("/api/predict")
def predict_pipeline_failure(

    pipeline:
        schemas.FailurePredictionRequest,

    db: Session = Depends(get_db)
):

    result = predict_failure(

        build_time=
            pipeline.build_time,

        tests_failed=
            pipeline.tests_failed,

        cpu_usage=
            pipeline.cpu_usage,

        memory_usage=
            pipeline.memory_usage,

        vulnerabilities=
            pipeline.vulnerabilities
    )

    prediction = (
        result["prediction"]
    )

    new_prediction = (
        models.FailurePrediction(

            build_time=
                pipeline.build_time,

            tests_failed=
                pipeline.tests_failed,

            cpu_usage=
                pipeline.cpu_usage,

            memory_usage=
                pipeline.memory_usage,

            vulnerabilities=
                pipeline.vulnerabilities,

            predicted_status=
                prediction[
                    "predicted_status"
                ],

            failure_probability=
                prediction[
                    "failure_probability"
                ],

            success_probability=
                prediction[
                    "success_probability"
                ],

            confidence=
                prediction[
                    "confidence"
                ],

            risk_level=
                prediction[
                    "risk_level"
                ]
        )
    )

    db.add(
        new_prediction
    )

    db.commit()

    db.refresh(
        new_prediction
    )

    return {

        "prediction_id":
            new_prediction.id,

        "input": {

            "build_time":
                pipeline.build_time,

            "tests_failed":
                pipeline.tests_failed,

            "cpu_usage":
                pipeline.cpu_usage,

            "memory_usage":
                pipeline.memory_usage,

            "vulnerabilities":
                pipeline.vulnerabilities
        },

        "analysis":
            result,

        "saved_to_database":
            True
    }


# ============================================================
# ML PREDICTION HISTORY
# ============================================================

@app.get("/api/predictions/history")
def get_prediction_history(
    db: Session = Depends(get_db)
):

    predictions = (

        db.query(
            models.FailurePrediction
        )

        .order_by(
            models.FailurePrediction.id.desc()
        )

        .all()
    )

    return [

        {
            "id":
                prediction.id,

            "build_time":
                prediction.build_time,

            "tests_failed":
                prediction.tests_failed,

            "cpu_usage":
                prediction.cpu_usage,

            "memory_usage":
                prediction.memory_usage,

            "vulnerabilities":
                prediction.vulnerabilities,

            "predicted_status":
                prediction.predicted_status,

            "failure_probability":
                prediction.failure_probability,

            "success_probability":
                prediction.success_probability,

            "confidence":
                prediction.confidence,

            "risk_level":
                prediction.risk_level,

            "created_at":
                prediction.created_at
        }

        for prediction
        in predictions
    ]


# ============================================================
# LATEST ML PREDICTION
# ============================================================

@app.get("/api/predictions/latest")
def get_latest_prediction(
    db: Session = Depends(get_db)
):

    prediction = (

        db.query(
            models.FailurePrediction
        )

        .order_by(
            models.FailurePrediction.id.desc()
        )

        .first()
    )

    if prediction is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "No ML predictions found"
            )
        )

    return {

        "id":
            prediction.id,

        "build_time":
            prediction.build_time,

        "tests_failed":
            prediction.tests_failed,

        "cpu_usage":
            prediction.cpu_usage,

        "memory_usage":
            prediction.memory_usage,

        "vulnerabilities":
            prediction.vulnerabilities,

        "predicted_status":
            prediction.predicted_status,

        "failure_probability":
            prediction.failure_probability,

        "success_probability":
            prediction.success_probability,

        "confidence":
            prediction.confidence,

        "risk_level":
            prediction.risk_level,

        "created_at":
            prediction.created_at
    }


# ============================================================
# DASHBOARD OVERVIEW
# ============================================================

@app.get("/api/dashboard/overview")
def dashboard_overview(
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Latest pipeline
    # --------------------------------------------------------

    latest_pipeline = (

        db.query(
            models.PipelineRun
        )

        .order_by(
            models.PipelineRun.id.desc()
        )

        .first()
    )


    # --------------------------------------------------------
    # Latest security scan
    # --------------------------------------------------------

    latest_security = (

        db.query(
            models.SecurityScan
        )

        .order_by(
            models.SecurityScan.id.desc()
        )

        .first()
    )


    # --------------------------------------------------------
    # Latest ML prediction
    # --------------------------------------------------------

    latest_prediction = (

        db.query(
            models.FailurePrediction
        )

        .order_by(
            models.FailurePrediction.id.desc()
        )

        .first()
    )


    # --------------------------------------------------------
    # Latest complexity result
    # --------------------------------------------------------

    latest_complexity = (

        db.query(
            models.CodeAnalysis
        )

        .order_by(
            models.CodeAnalysis.id.desc()
        )

        .first()
    )


    # --------------------------------------------------------
    # OVERALL RISK
    # --------------------------------------------------------

    risk_priority = {

        "No data": 0,
        "Safe": 0,
        "Minimal": 0,
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4
    }


    security_risk = (

        latest_security.risk_level

        if latest_security

        else "No data"
    )


    prediction_risk = (

        latest_prediction.risk_level

        if latest_prediction

        else "No data"
    )


    if (
        latest_security
        and latest_security.critical > 0
    ):

        overall_risk = "Critical"

    elif (
        risk_priority.get(
            prediction_risk,
            0
        )
        >=
        risk_priority.get(
            security_risk,
            0
        )
    ):

        overall_risk = (
            prediction_risk
        )

    else:

        overall_risk = (
            security_risk
        )


    # --------------------------------------------------------
    # DASHBOARD RESPONSE
    # --------------------------------------------------------

    return {

        "project":
            "AI CI/CD DevSecOps Assistant",


        # ====================================================
        # PIPELINE
        # ====================================================

        "pipeline": {

            "pipeline_id":

                latest_pipeline.pipeline_id
                if latest_pipeline
                else None,


            "status":

                latest_pipeline.status
                if latest_pipeline
                else "No data",


            "build_time":

                latest_pipeline.build_time
                if latest_pipeline
                else 0,


            "tests_passed":

                latest_pipeline.tests_passed
                if latest_pipeline
                else 0,


            "tests_failed":

                latest_pipeline.tests_failed
                if latest_pipeline
                else 0,


            "cpu_usage":

                latest_pipeline.cpu_usage
                if latest_pipeline
                else 0,


            "memory_usage":

                latest_pipeline.memory_usage
                if latest_pipeline
                else 0,


            "vulnerabilities":

                latest_pipeline.vulnerabilities
                if latest_pipeline
                else 0
        },


        # ====================================================
        # SECURITY
        # ====================================================

        "security": {

            "security_score":

                latest_security.security_score
                if latest_security
                else None,


            "risk_level":

                latest_security.risk_level
                if latest_security
                else "No data",


            "critical":

                latest_security.critical
                if latest_security
                else 0,


            "high":

                latest_security.high
                if latest_security
                else 0,


            "medium":

                latest_security.medium
                if latest_security
                else 0,


            "low":

                latest_security.low
                if latest_security
                else 0,


            "vulnerabilities":

                latest_security.vulnerabilities
                if latest_security
                else 0,


            "secrets":

                latest_security.secrets
                if latest_security
                else 0,


            "misconfigurations":

                latest_security.misconfigurations
                if latest_security
                else 0
        },


        # ====================================================
        # MACHINE LEARNING
        # ====================================================

        "ml_prediction": {

            "predicted_status":

                latest_prediction.predicted_status
                if latest_prediction
                else "No prediction",


            "failure_probability":

                latest_prediction.failure_probability
                if latest_prediction
                else 0,


            "success_probability":

                latest_prediction.success_probability
                if latest_prediction
                else 0,


            "confidence":

                latest_prediction.confidence
                if latest_prediction
                else 0,


            "risk_level":

                latest_prediction.risk_level
                if latest_prediction
                else "No data"
        },


        # ====================================================
        # COMPLEXITY
        # ====================================================

        "complexity": {

            "file":

                latest_complexity.file_name
                if latest_complexity
                else None,


            "time_complexity":

                latest_complexity.time_complexity
                if latest_complexity
                else "Not analyzed",


            "space_complexity":

                latest_complexity.space_complexity
                if latest_complexity
                else "Not analyzed"
        },


        # ====================================================
        # OVERALL SYSTEM RISK
        # ====================================================

        "overall_risk":
            overall_risk
    }