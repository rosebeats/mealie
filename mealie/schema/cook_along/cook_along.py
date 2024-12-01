from typing import Literal

from mealie.schema._mealie import MealieModel


class AIUserMessage(MealieModel):
    """A message from the user asking a question from the assistant"""

    content: str
    """The message from the user"""
    role: Literal["user"] = "user"
    """The role of the message (user)"""


class AIAssistantMessage(MealieModel):
    """A message from the assistant answering a question from the user"""

    content: str
    """The response from the assistant"""
    role: Literal["assistant"] = "assistant"
    """The role of the message (assistant)"""


def open_ai_to_message(message: dict):
    """Turn a dictionary message into a pydantic object. Supports user and assistant messages."""
    content = message.get("content")
    match message.get("role"):
        case "user":
            return AIUserMessage(content=content)
        case "assistant":
            return AIAssistantMessage(content=content)
