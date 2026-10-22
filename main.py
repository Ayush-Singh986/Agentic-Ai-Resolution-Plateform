from fastapi import FastAPI

from app.api.routes import router

from app.monitoring.metrics import (
    initialize_metrics
)

initialize_metrics()

app = FastAPI(
    title="AI Incident Resolution Platform"
)

app.include_router(router)