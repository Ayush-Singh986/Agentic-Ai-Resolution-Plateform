import time

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends

from app.schemas.incident import (
    IncidentRequest,
    IncidentResponse,
    RemediationActionRequest,
    RemediationRequestListResponse,
    RemediationRequestResponse,
)
from app.security.cognito_auth import (
    require_approver,
    require_cognito_user,
)
from app.services.aws_remediation import (
    approve_remediation_request,
    create_remediation_request,
    get_remediation_status,
    list_pending_remediation_requests,
    reject_remediation_request,
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


@router.post(
    "/remediation-requests",
    response_model=RemediationRequestResponse,
)
def create_remediation(
    request: RemediationActionRequest,
    claims: dict = Depends(require_cognito_user),
):
    return create_remediation_request(
        incident_id=request.incident_id,
        action=request.action,
        created_by=claims["sub"],
    )


@router.post(
    "/remediation-requests/{request_id}/approve",
    response_model=RemediationRequestResponse,
)
def approve_remediation(
    request_id: str,
    claims: dict = Depends(require_approver),
):
    from app.services.aws_remediation import get_remediation_request

    request = get_remediation_request(request_id)
    if request["created_by"] == claims["sub"]:
        raise HTTPException(
            status_code=403,
            detail="A different approver must approve this request.",
        )
    return approve_remediation_request(
        request_id=request_id,
        approved_by=claims["sub"],
    )


@router.get(
    "/remediation-requests/pending",
    response_model=RemediationRequestListResponse,
)
def list_pending_remediations(
    claims: dict = Depends(require_approver),
):
    return {"requests": list_pending_remediation_requests()}


@router.get(
    "/remediation-requests/{request_id}",
    response_model=RemediationRequestResponse,
)
def remediation_status(
    request_id: str,
    claims: dict = Depends(require_cognito_user),
):
    return get_remediation_status(request_id)


@router.post(
    "/remediation-requests/{request_id}/reject",
    response_model=RemediationRequestResponse,
)
def reject_remediation(
    request_id: str,
    claims: dict = Depends(require_approver),
):
    return reject_remediation_request(
        request_id=request_id,
        rejected_by=claims["sub"],
    )