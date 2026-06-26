from langchain_core.messages import HumanMessage, AIMessage
from src.config import LLM_MODEL, LLM_TEMPERATURE
from src.graph.state import AgentState
from src.agents.supervisor import create_supervisor_agent
from src.agents.billing import create_billing_agent
from src.agents.technical import create_technical_agent
from src.agents.escalation import create_escalation_agent


def _get_llm():
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)


def supervisor_node(state: AgentState) -> dict:
    llm = _get_llm()
    route_query = create_supervisor_agent(llm)
    decision = route_query(state["user_input"])

    return {
        "current_agent": "supervisor",
        "routing_decision": decision,
        "messages": [AIMessage(content=f"[Supervisor] Routing to {decision} agent")],
        "turn_count": state.get("turn_count", 0) + 1,
    }


def billing_node(state: AgentState) -> dict:
    llm = _get_llm()
    handle_request = create_billing_agent(llm)
    result = handle_request(state["user_input"], state.get("user_email", ""))

    return {
        "current_agent": "billing",
        "agent_response": result["response"],
        "ticket_created": result["ticket_created"],
        "ticket_id": result.get("ticket_id"),
        "articles_found": result["articles_found"],
        "messages": [AIMessage(content=result["response"])],
        "turn_count": state.get("turn_count", 0) + 1,
    }


def technical_node(state: AgentState) -> dict:
    llm = _get_llm()
    handle_request = create_technical_agent(llm)
    result = handle_request(state["user_input"], state.get("user_email", ""))

    return {
        "current_agent": "technical",
        "agent_response": result["response"],
        "ticket_created": result["ticket_created"],
        "ticket_id": result.get("ticket_id"),
        "articles_found": result["articles_found"],
        "messages": [AIMessage(content=result["response"])],
        "turn_count": state.get("turn_count", 0) + 1,
    }


def escalation_node(state: AgentState) -> dict:
    llm = _get_llm()
    handle_request = create_escalation_agent(llm)
    result = handle_request(state["user_input"], state.get("user_email", ""))

    return {
        "current_agent": "escalation",
        "agent_response": result["response"],
        "ticket_created": result["ticket_created"],
        "ticket_id": result.get("ticket_id"),
        "escalation_priority": result.get("priority"),
        "articles_found": 0,
        "messages": [AIMessage(content=result["response"])],
        "turn_count": state.get("turn_count", 0) + 1,
    }
