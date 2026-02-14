from langgraph.graph import StateGraph, END
from backend.agents import (
    query_analysis_agent,
    retrieval_agent,
    generation_agent,
    rerank_agent,
    citation_agent
)


def route_retrieval(state):
    """
    Conditional routing function.
    Decides which retrieval path to take.
    """
    if state.get("use_web"):
        return "retrieval"   # same retrieval node handles web internally
    return "retrieval"


def build_graph():

    workflow = StateGraph(dict)

    # ------------------
    # Add Nodes
    # ------------------
    workflow.add_node("analysis", query_analysis_agent)
    workflow.add_node("retrieval", retrieval_agent)
    workflow.add_node("rerank", rerank_agent)
    workflow.add_node("generation", generation_agent)
    workflow.add_node("citation", citation_agent)

    # ------------------
    # Entry Point
    # ------------------
    workflow.set_entry_point("analysis")

    # ------------------
    # Conditional Edge
    # ------------------
    workflow.add_conditional_edges(
        "analysis",
        route_retrieval
    )

    # ------------------
    # Normal Flow
    # ------------------
    workflow.add_edge("retrieval", "rerank")
    workflow.add_edge("rerank", "generation")
    workflow.add_edge("generation", "citation")
    workflow.add_edge("citation", END)

    return workflow.compile()


graph = build_graph()
