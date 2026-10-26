from typing import TypedDict, List, Optional


class IncidentState(TypedDict):

    incident_id: str
    title: str
    priority: str
    description: str

    masked_description: str

    severity: str
    domain: str

    retrieved_context: List[str]

    root_cause: str
    remediation_plan: List[str]

    confidence_score: float

    hallucination_detected: bool

    requires_human_review: bool

    rca_prompt_version: str
    
    planner_prompt_version: str

    final_response: Optional[dict]