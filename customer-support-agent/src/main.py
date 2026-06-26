from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from src.graph.builder import build_support_graph, get_default_state

app = FastAPI(title="Multi-Agent Customer Support System", version="1.0.0")

graph = build_support_graph()


class SupportRequest(BaseModel):
    message: str
    email: str = ""


class SupportResponse(BaseModel):
    response: str
    agent_type: str
    ticket_created: bool
    ticket_id: str | None = None
    articles_found: int = 0
    escalation_priority: str | None = None


@app.get("/health")
def health_check():
    return {"status": "ok", "system": "Multi-Agent Customer Support"}


@app.post("/chat", response_model=SupportResponse)
def chat(request: SupportRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Il messaggio non può essere vuoto.")

    state = get_default_state()
    state["user_input"] = request.message
    state["user_email"] = request.email

    try:
        result = graph.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nell'elaborazione: {str(e)}")

    return SupportResponse(
        response=result.get("agent_response", "Nessuna risposta generata."),
        agent_type=result.get("current_agent", "unknown"),
        ticket_created=result.get("ticket_created", False),
        ticket_id=result.get("ticket_id"),
        articles_found=result.get("articles_found", 0),
        escalation_priority=result.get("escalation_priority"),
    )


@app.post("/cli")
def cli_chat():
    print("=" * 60)
    print("  Multi-Agent Customer Support System (LangGraph)")
    print("  Scrivi 'exit' per uscire")
    print("=" * 60)
    print()

    while True:
        user_input = input("\nTu: ").strip()
        if user_input.lower() in ("exit", "quit", "esci"):
            print("Arrivederci!")
            break

        state = get_default_state()
        state["user_input"] = user_input

        result = graph.invoke(state)

        agent = result.get("current_agent", "?").upper()
        response = result.get("agent_response", "Nessuna risposta.")

        print(f"\n[{agent}]: {response}")

        if result.get("ticket_created"):
            print(f"  [Ticket #{result['ticket_id']} creato]")
        if result.get("articles_found"):
            print(f"  [Knowledge base: {result['articles_found']} articoli trovati]")
        if result.get("escalation_priority"):
            print(f"  [Priorità escalation: {result['escalation_priority'].upper()}]")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
