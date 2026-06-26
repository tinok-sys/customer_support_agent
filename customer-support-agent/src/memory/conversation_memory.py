from typing import Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class ConversationMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.messages: list[BaseMessage] = []
        self.summary: Optional[str] = None

    def add_message(self, message: BaseMessage):
        self.messages.append(message)
        if len(self.messages) > self.max_turns * 2:
            self._summarize_oldest()

    def get_messages(self) -> list[BaseMessage]:
        return self.messages

    def clear(self):
        self.messages.clear()
        self.summary = None

    def _summarize_oldest(self):
        oldest = self.messages[:4]
        summary_text = "; ".join(
            f"{'User' if isinstance(m, HumanMessage) else 'Agent'}: {m.content[:100]}"
            for m in oldest
        )
        self.summary = f"[Previous conversation summary: {summary_text}]"
        self.messages = self.messages[4:]

    def get_context(self) -> str:
        context = ""
        if self.summary:
            context += self.summary + "\n"
        for msg in self.messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            context += f"{role}: {msg.content}\n"
        return context
