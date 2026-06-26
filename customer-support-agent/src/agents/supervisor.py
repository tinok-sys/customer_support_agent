from langchain_core.messages import SystemMessage, HumanMessage
from src.config import LLM_MODEL, LLM_TEMPERATURE


SUPERVISOR_PROMPT = """Sei un supervisore del supporto clienti. Il tuo compito è analizzare la richiesta dell'utente e decidere quale agente specializzato deve gestirla.

Categorie disponibili:
- **billing**: richieste di fatturazione, rimborsi, pagamenti, piani, upgrade/downgrade, metodi di pagamento
- **technical**: problemi tecnici, bug, errori, API, troubleshooting, configurazione
- **escalation**: reclami urgenti, richieste che richiedono intervento umano, situazioni non risolvibili dagli altri agenti, linguaggio offensivo

Rispondi SOLO con il nome della categoria: billing, technical, o escalation.
Non aggiungere spiegazioni, solo il nome della categoria."""


def create_supervisor_agent(llm):
    def route_query(user_input: str) -> str:
        messages = [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=f"Richiesta utente: {user_input}"),
        ]
        response = llm.invoke(messages)
        decision = response.content.strip().lower()

        if "billing" in decision:
            return "billing"
        elif "technical" in decision:
            return "technical"
        else:
            return "escalation"

    return route_query
