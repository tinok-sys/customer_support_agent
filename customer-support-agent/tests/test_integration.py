from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from src.agents.supervisor import create_supervisor_agent
from src.agents.billing import create_billing_agent
from src.agents.technical import create_technical_agent
from src.agents.escalation import create_escalation_agent
from src.graph.builder import build_support_graph, get_default_state
from src.graph.nodes import supervisor_node
from src.memory.conversation_memory import ConversationMemory


def _mock_llm(content: str):
    mock = MagicMock()
    mock.invoke.return_value = AIMessage(content=content)
    return mock


class TestSupervisorRouting:
    @pytest.mark.parametrize("input_text,expected", [
        ("Voglio un rimborso per la fattura INV-001", "billing"),
        ("Non riesco a pagare con la carta di credito", "billing"),
        ("Come faccio a fare l'upgrade del mio piano?", "billing"),
        ("Il sito mi da errore 500 quando carico", "technical"),
        ("La API non funziona, ricevo errore 401", "technical"),
        ("Ho dimenticato la password", "technical"),
        ("URGENTE: ho perso accesso al mio account", "escalation"),
        ("Voglio parlare con un operatore umano", "escalation"),
    ])
    def test_supervisor_routes_correctly(self, input_text, expected):
        mock_llm = _mock_llm(expected)
        route_query = create_supervisor_agent(mock_llm)
        decision = route_query(input_text)
        assert decision == expected

    def test_supervisor_falls_back_to_escalation(self):
        mock_llm = _mock_llm("non ho capito")
        route_query = create_supervisor_agent(mock_llm)
        decision = route_query("richiesta incomprensibile")
        assert decision == "escalation"


class TestBillingAgent:
    def test_handles_refund_request(self):
        mock_llm = _mock_llm("Ho processato il rimborso per la fattura INV-001")
        handle_request = create_billing_agent(mock_llm)
        result = handle_request("Voglio un rimborso", "mario@example.com")
        assert result["agent_type"] == "billing"
        assert "rimborso" in result["response"].lower()
        assert result["ticket_created"] is False

    def test_creates_ticket_when_needed(self):
        mock_llm = _mock_llm("Ho creato un ticket per la sua richiesta di rimborso")
        handle_request = create_billing_agent(mock_llm)
        result = handle_request("Problema complesso di fatturazione", "luca@test.com")
        assert result["ticket_created"] is True
        assert result["ticket_id"] is not None
        assert result["ticket_id"].startswith("TKT-")

    def test_without_email_still_works(self):
        mock_llm = _mock_llm("Richiesta processata")
        handle_request = create_billing_agent(mock_llm)
        result = handle_request("Voglio informazioni sul mio abbonamento")
        assert result["agent_type"] == "billing"


class TestTechnicalAgent:
    def test_handles_error_query(self):
        mock_llm = _mock_llm("Ecco come risolvere l'errore 500. Provi a svuotare la cache.")
        handle_request = create_technical_agent(mock_llm)
        result = handle_request("Ho errore 500", "tecnico@test.com")
        assert result["agent_type"] == "technical"
        assert "errore" in result["response"].lower()

    def test_handles_api_rate_limit_query(self):
        mock_llm = _mock_llm("Ecco le informazioni sui rate limit API.")
        handle_request = create_technical_agent(mock_llm)
        result = handle_request("API rate limit", "dev@test.com")
        assert result["agent_type"] == "technical"
        assert result["articles_found"] > 0

    def test_ticket_on_complex_issue(self):
        mock_llm = _mock_llm("Problema complesso, creo un ticket tecnico per i nostri ingegneri.")
        handle_request = create_technical_agent(mock_llm)
        result = handle_request("Il database crasha ogni ora")
        assert result["ticket_created"] is True


class TestEscalationAgent:
    def test_escalation_with_urgent_priority(self):
        mock_llm = _mock_llm("La sua richiesta urgente è stata presa in carico.")
        handle_request = create_escalation_agent(mock_llm)
        result = handle_request("URGENTE: violazione della sicurezza", "admin@azienda.com")
        assert result["agent_type"] == "escalation"
        assert result["ticket_created"] is True
        assert result["priority"] == "urgente"

    def test_escalation_with_normal_priority(self):
        mock_llm = _mock_llm("Un operatore umano la contatterà presto.")
        handle_request = create_escalation_agent(mock_llm)
        result = handle_request("Voglio parlare con un responsabile", "user@test.com")
        assert result["ticket_created"] is True
        assert result["priority"] == "alta"


class TestGraphExecution:
    def build_mock_graph(self, routing_decision):
        mock_llm = _mock_llm(routing_decision)
        graph = build_support_graph()

        with patch("src.graph.nodes._get_llm", return_value=mock_llm):
            state = get_default_state()
            state["user_input"] = "Richiesta di test"
            state["user_email"] = "test@example.com"
            result = graph.invoke(state)

        return result

    def test_graph_routes_to_billing(self):
        mock_llm = _mock_llm("billing")
        graph = build_support_graph()

        with patch("src.graph.nodes._get_llm", return_value=mock_llm):
            state = get_default_state()
            state["user_input"] = "Voglio un rimborso"
            state["user_email"] = "mario@example.com"
            result = graph.invoke(state)

        assert result["current_agent"] in ("billing", "supervisor")
        assert "routing_decision" in result

    def test_graph_with_empty_input(self):
        graph = build_support_graph()

        with patch("src.graph.nodes._get_llm") as mock_factory:
            mock_llm = _mock_llm("technical")
            mock_factory.return_value = mock_llm

            state = get_default_state()
            state["user_input"] = "Help"
            state["user_email"] = ""
            result = graph.invoke(state)

        assert result is not None


class TestGraphNodes:
    def test_supervisor_node_no_api_key(self):
        mock_llm = _mock_llm("billing")

        with patch("src.graph.nodes._get_llm", return_value=mock_llm):
            state = get_default_state()
            state["user_input"] = "Voglio un rimborso"
            state["user_email"] = "test@example.com"
            result = supervisor_node(state)

        assert result["current_agent"] == "supervisor"
        assert result["routing_decision"] == "billing"


class TestMemoryIntegration:
    def test_conversation_memory_context(self):
        from src.memory.conversation_memory import ConversationMemory

        memory = ConversationMemory(max_turns=2)
        memory.add_message(HumanMessage(content="Ciao, ho un problema"))
        memory.add_message(AIMessage(content="Certo, mi dica pure"))
        memory.add_message(HumanMessage(content="Voglio un rimborso"))

        context = memory.get_context()
        assert "Ciao" in context
        assert "rimborso" in context

    def test_memory_summarization(self):
        memory = ConversationMemory(max_turns=2)
        for i in range(6):
            memory.add_message(HumanMessage(content=f"Messaggio {i}"))
            memory.add_message(AIMessage(content=f"Risposta {i}"))

        assert memory.summary is not None
        assert len(memory.get_messages()) <= 4
