from pydantic import BaseModel


class IncidentRequest(BaseModel):
    incident_id: str
    title: str
    description: str


class IncidentResponse(BaseModel):
    incident_id: str
    severity: str
    domain: str
    root_cause: str
    remediation_plan: str
    confidence_score: float