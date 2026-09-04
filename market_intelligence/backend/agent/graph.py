from langgraph.graph import StateGraph, END
from agent.state import MarketResearchState
from market_intelligence.backend.agent.nodes import scout_node, analyst_node, critic_node

def route_after_critic(state: MarketResearchState) -> str:
    """Conditional Edge: Loop back to Scout if critique failed, else finish."""
    if state.get("critique_feedback") and state.get("search_retry_count", 0) < 2:
        return "scout"
    return END

def build_graph():
    workflow = StateGraph(MarketResearchState)

    # Add Nodes
    workflow.add_node("scout", scout_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("critic", critic_node)

    # Set Entry Point & Connections
    workflow.set_entry_point("scout")
    workflow.add_edge("scout", "analyst")
    workflow.add_edge("analyst", "critic")
    
    # Conditional Loop Node
    workflow.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "scout": "scout",
            END: END
        }
    )

    return workflow.compile()

app_graph = build_graph()