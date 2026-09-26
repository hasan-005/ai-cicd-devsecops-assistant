from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime
)

from .database import Base


# ============================================================
# PIPELINE RUN MODEL
# ============================================================

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    pipeline_id = Column(
        Integer,
        unique=True,
        index=True
    )

    status = Column(String)

    build_time = Column(Float)

    tests_passed = Column(Integer)

    tests_failed = Column(Integer)

    cpu_usage = Column(Float)

    memory_usage = Column(Float)

    vulnerabilities = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# SECURITY SCAN MODEL
# ============================================================

class SecurityScan(Base):
    __tablename__ = "security_scans"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    critical = Column(
        Integer,
        default=0
    )

    high = Column(
        Integer,
        default=0
    )

    medium = Column(
        Integer,
        default=0
    )

    low = Column(
        Integer,
        default=0
    )

    vulnerabilities = Column(
        Integer,
        default=0
    )

    secrets = Column(
        Integer,
        default=0
    )

    misconfigurations = Column(
        Integer,
        default=0
    )

    security_score = Column(
        Integer,
        default=100
    )

    risk_level = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# ML FAILURE PREDICTION MODEL
# ============================================================

class FailurePrediction(Base):
    __tablename__ = "failure_predictions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    build_time = Column(Float)

    tests_failed = Column(Integer)

    cpu_usage = Column(Float)

    memory_usage = Column(Float)

    vulnerabilities = Column(Integer)

    predicted_status = Column(String)

    failure_probability = Column(Float)

    success_probability = Column(Float)

    confidence = Column(Float)

    risk_level = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# CODE COMPLEXITY ANALYSIS MODEL
# ============================================================

class CodeAnalysis(Base):
    __tablename__ = "code_analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_name = Column(String)

    time_complexity = Column(String)

    space_complexity = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )