from langchain_core.messages import SystemMessage, HumanMessage
from src.tools.knowledge_base import search_knowledge_base
from src.tools.ticketing import create_ticket


TECHNICAL_PROMPT = """Sei un agente di supporto tecnico. Rispondi in italiano, in modo chiaro e strutturato.

Linee guida:
- Fornisci soluzioni passo-passo
- Se il problema è complesso, chiedi chiarimenti
- Usa la knowledge base per trovare articoli rilevanti
- Crea un ticket se necessario

Strumenti:
1. search_knowledge_base(query, category="technical") - cerca articoli tecnici
2. create_ticket(email, issue_type, description) - crea ticket di supporto

Categorie: "technical" per articoli della knowledge base."""


def create_technical_agent(llm):
    def handle_request(user_input: str, email: str = "") -> dict:
        kb_results = search_knowledge_base(user_input, category="technical")

        kb_context = ""
        if kb_results:
            kb_context = "Articoli trovati:\n" + "\n".join(
                f"- {a.title}: {a.content[:200]}..." for a in kb_results[:3]
            )

        messages = [
            SystemMessage(content=f"{TECHNICAL_PROMPT}\n\n{ kb_context if kb_context else 'Nessun articolo trovato nella knowledge base.'}"),
            HumanMessage(content=f"Problema tecnico: {user_input}\nEmail: {email or 'non fornita'}"),
        ]

        response = llm.invoke(messages)

        result = {
            "response": response.content,
            "ticket_created": False,
            "articles_found": len(kb_results),
            "agent_type": "technical",
        }

        if "ticket" in response.content.lower():
            ticket = create_ticket(
                customer_email=email or "unknown@example.com",
                issue_type="technical",
                description=user_input,
            )
            result["ticket_created"] = True
            result["ticket_id"] = ticket.ticket_id

        return result

    return handle_request
