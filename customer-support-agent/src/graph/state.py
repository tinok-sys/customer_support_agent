from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
    user_email: str
    current_agent: str
    routing_decision: str
    agent_response: Optional[str]
    ticket_created: bool
    ticket_id: Optional[str]
    escalation_priority: Optional[str]
    articles_found: int
    conversation_summary: Optional[str]
    turn_count: int
    max_turns: int
