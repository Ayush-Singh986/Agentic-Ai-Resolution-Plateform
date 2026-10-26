from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class IncidentRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    incident_id: str = Field(
        min_length=1,
        max_length=100,
    )
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str = Field(
        min_length=1,
        max_length=10000,
    )


class TicketDraft(BaseModel):
    status: Literal["draft"]
    title: str
    priority: str
    labels: list[str]
    description: str


class IncidentResponse(BaseModel):
    incident_id: str
    severity: str
    domain: str
    priority: str
    root_cause: str
    remediation_plan: list[str]
    confidence_score: float
    hallucination_detected: bool
    requires_human_review: bool
    remediation_executed: bool
    evidence: list[str]
    ticket_draft: TicketDraft
    prompt_versions: dict[str, str]