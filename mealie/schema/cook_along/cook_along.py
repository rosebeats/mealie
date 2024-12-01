from typing import Literal

from mealie.schema._mealie import MealieModel


class AIUserMessage(MealieModel):
    content: str
    role: Literal["user"] = "user"


class AIAssistantMessage(MealieModel):
    content: str
    role: Literal["assistant"] = "assistant"


def open_ai_to_message(message: dict):
    content = message.get("content")
    match message.get("role"):
        case "user":
            return AIUserMessage(content=content)
        case "assistant":
            return AIAssistantMessage(content=content)
