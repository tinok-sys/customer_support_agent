from langchain_core.messages import SystemMessage, HumanMessage
from src.tools.ticketing import create_ticket


ESCALATION_PROMPT = """Sei l'agente di escalation. Il cliente ha una richiesta che richiede un intervento umano.

Il tuo compito:
1. Spiega educatamente che la richiesta verrà presa in carico da un operatore umano
2. Crea un ticket di escalation con priorità alta
3. Rassicura il cliente che verrà ricontattato

Priorità:
- "urgente" se ci sono parole come "urgente", "immediato", "perdita", "sicurezza", "violazione"
- "alta" per reclami, problemi non risolti
- "normale" per tutto il resto"""


def create_escalation_agent(llm):
    def handle_request(user_input: str, email: str = "") -> dict:
        urgent_keywords = ["urgente", "immediato", "perdita", "sicurezza", "violazione", "hacker"]
        priority = "urgente" if any(kw in user_input.lower() for kw in urgent_keywords) else "alta"

        ticket = create_ticket(
            customer_email=email or "unknown@example.com",
            issue_type="escalation",
            description=f"[{priority.upper()}] {user_input}",
        )

        messages = [
            SystemMessage(content=ESCALATION_PROMPT),
            HumanMessage(content=f"Richiesta da escalare: {user_input}\nEmail: {email or 'non fornita'}\nPriorità: {priority}"),
        ]

        response = llm.invoke(messages)

        return {
            "response": response.content,
            "ticket_created": True,
            "ticket_id": ticket.ticket_id,
            "priority": priority,
            "articles_found": 0,
            "agent_type": "escalation",
        }

    return handle_request
