import time

from fastapi import APIRouter
from fastapi import HTTPException

from app.schemas.incident import (
    IncidentRequest,
    IncidentResponse,
)

from app.security.pii_masking import (
    mask_pii
)

from app.security.prompt_injection import (
    detect_prompt_injection
)

from app.graph.workflow import (
    graph
)

from app.events.kafka_producer import (
    publish_event
)

from app.memory.redis_memory import (
    save_incident_memory
)

from app.monitoring.metrics import (
    incident_counter,
    latency_metric
)

router = APIRouter()


@router.get("/health")
def health():

    return {
        "status": "healthy"
    }


@router.post(
    "/incident",
    response_model=IncidentResponse,
)

def process_incident(
        request: IncidentRequest
):

    start = time.time()

    incident_counter.inc()

    if detect_prompt_injection(
            request.description):

        raise HTTPException(
            status_code=400,
            detail="Prompt Injection Detected"
        )

    state = {

        "incident_id":
            request.incident_id,

        "title":
            request.title,

        "description":
            request.description,

        "masked_description":
            mask_pii(
                request.description
            ),

        "retrieved_context": [],

        "severity": "",

        "domain": "",

        "root_cause": "",

        "remediation_plan": [],

        "confidence_score": 0.0,

        "hallucination_detected":
            False,

        "final_response": None
    }

    result = graph.invoke(
        state
    )

    response = result[
        "final_response"
    ]

    save_incident_memory(
        request.incident_id,
        response
    )

    publish_event(
        response
    )

    latency_metric.observe(
        time.time() - start
    )

    return response