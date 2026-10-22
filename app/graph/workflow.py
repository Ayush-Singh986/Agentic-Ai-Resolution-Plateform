from langgraph.graph import (
    StateGraph,
    END
)

from app.graph.state import (
    IncidentState
)

from app.agents.triage_agent import (
    run_triage_agent
)

from app.agents.retrieval_agent import (
    run_retrieval_agent
)

from app.agents.rca_agent import (
    run_rca_agent
)

from app.agents.planner_agent import (
    run_planner_agent
)

from app.agents.validation_agent import (
    run_validation_agent
)

from app.agents.execution_agent import (
    run_execution_agent
)

workflow = StateGraph(
    IncidentState
)

workflow.add_node(
    "triage",
    run_triage_agent
)

workflow.add_node(
    "retrieval",
    run_retrieval_agent
)

workflow.add_node(
    "rca",
    run_rca_agent
)

workflow.add_node(
    "planner",
    run_planner_agent
)

workflow.add_node(
    "validation",
    run_validation_agent
)

workflow.add_node(
    "execution",
    run_execution_agent
)

workflow.set_entry_point(
    "triage"
)

workflow.add_edge(
    "triage",
    "retrieval"
)

workflow.add_edge(
    "retrieval",
    "rca"
)

workflow.add_edge(
    "rca",
    "planner"
)

workflow.add_edge(
    "planner",
    "validation"
)

workflow.add_edge(
    "validation",
    "execution"
)

workflow.add_edge(
    "execution",
    END
)

graph = workflow.compile()