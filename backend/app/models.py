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