from langgraph.graph import StateGraph, START, END
from src.graph.state import AgentState
from src.graph.nodes import supervisor_node, billing_node, technical_node, escalation_node


def router_condition(state: AgentState) -> str:
    decision = state.get("routing_decision", "")
    if decision == "billing":
        return "billing"
    elif decision == "technical":
        return "technical"
    else:
        return "escalation"


def build_support_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("billing", billing_node)
    builder.add_node("technical", technical_node)
    builder.add_node("escalation", escalation_node)

    builder.add_edge(START, "supervisor")

    builder.add_conditional_edges(
        "supervisor",
        router_condition,
        {
            "billing": "billing",
            "technical": "technical",
            "escalation": "escalation",
        },
    )

    builder.add_edge("billing", END)
    builder.add_edge("technical", END)
    builder.add_edge("escalation", END)

    return builder.compile()


def get_default_state() -> AgentState:
    return {
        "messages": [],
        "user_input": "",
        "user_email": "",
        "current_agent": "",
        "routing_decision": "",
        "agent_response": None,
        "ticket_created": False,
        "ticket_id": None,
        "escalation_priority": None,
        "articles_found": 0,
        "conversation_summary": None,
        "turn_count": 0,
        "max_turns": 10,
    }
