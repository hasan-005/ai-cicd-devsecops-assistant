from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class PipelineRunCreate(BaseModel):
    pipeline_id: int = Field(gt=0)

    status: str

    build_time: float = Field(ge=0)

    tests_passed: int = Field(ge=0)

    tests_failed: int = Field(ge=0)

    cpu_usage: float = Field(ge=0, le=100)

    memory_usage: float = Field(ge=0)

    vulnerabilities: int = Field(ge=0)


class PipelineRunResponse(PipelineRunCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FailurePredictionRequest(BaseModel):
    build_time: float = Field(ge=0)
    tests_failed: int = Field(ge=0)
    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0)
    vulnerabilities: int = Field(ge=0)