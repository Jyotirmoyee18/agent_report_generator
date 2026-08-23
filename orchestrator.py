from __future__ import annotations
from langgraph.graph import StateGraph, END

from state import ReportState
from agents import data_analysis_agent, vision_agent, generation_agent


def supervisor(state: ReportState) -> dict:
    """Decide which agent should run next based on current state."""
    completed = state.get("completed_agents", [])

    needs_data = state.get("data_path") and "data_analysis_agent" not in completed
    needs_vision = state.get("chart_image_paths") and "document_vision_agent" not in completed
    needs_generation = "generation_agent" not in completed

    if needs_data:
        next_agent = "data_analysis_agent"
    elif needs_vision:
        next_agent = "document_vision_agent"
    elif needs_generation:
        next_agent = "generation_agent"
    else:
        next_agent = "END"

    return {"next_agent": next_agent}


def _route(state: ReportState) -> str:
    return state.get("next_agent", "END")


def build_graph():
    graph = StateGraph(ReportState)

    graph.add_node("supervisor", supervisor)
    graph.add_node("data_analysis_agent", data_analysis_agent.run)
    graph.add_node("document_vision_agent", vision_agent.run)
    graph.add_node("generation_agent", generation_agent.run)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        _route,
        {
            "data_analysis_agent": "data_analysis_agent",
            "document_vision_agent": "document_vision_agent",
            "generation_agent": "generation_agent",
            "END": END,
        },
    )
    # every specialist agent reports back to the supervisor for the next decision
    graph.add_edge("data_analysis_agent", "supervisor")
    graph.add_edge("document_vision_agent", "supervisor")
    graph.add_edge("generation_agent", "supervisor")

    return graph.compile()
