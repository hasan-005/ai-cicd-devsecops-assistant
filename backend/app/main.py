from fastapi import FastAPI


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