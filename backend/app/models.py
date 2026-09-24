from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from .database import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)

    pipeline_id = Column(Integer, unique=True, index=True)

    status = Column(String)

    build_time = Column(Float)

    tests_passed = Column(Integer)

    tests_failed = Column(Integer)

    cpu_usage = Column(Float)

    memory_usage = Column(Float)

    vulnerabilities = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

class SecurityScan(Base):
    __tablename__ = "security_scans"

    id = Column(Integer, primary_key=True, index=True)

    critical = Column(Integer, default=0)
    high = Column(Integer, default=0)
    medium = Column(Integer, default=0)
    low = Column(Integer, default=0)

    vulnerabilities = Column(Integer, default=0)
    secrets = Column(Integer, default=0)
    misconfigurations = Column(Integer, default=0)

    security_score = Column(Integer, default=100)

    risk_level = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)