import itertools
import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from openai.resources.chat.completions import ChatCompletionMessageParam

from mealie.schema.recipe.recipe import Recipe
from mealie.services._base_service import BaseService
from mealie.services.cook_along import CookAlongMessagingService

PROMPTS_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "prompts"


class CookAlongService(BaseService):
    message_history: list[ChatCompletionMessageParam] = []
    messaging_service: CookAlongMessagingService
    recipe: Recipe

    def __init__(self, recipe: Recipe, messaging_service: CookAlongMessagingService) -> None:
        self.messaging_service = messaging_service
        self.recipe = recipe
        super().__init__()

    def build_prompt(self) -> ChatCompletionMessageParam:
        env = Environment(loader=FileSystemLoader(PROMPTS_DIR))
        template = env.get_template("system_prompt.jinja")
        model_params = {
            "description": self.recipe.description,
            "ingredients": "\n".join([ingredient.display for ingredient in self.recipe.recipe_ingredient]),
            "instructions": "\n\n".join([self.join_title_text(step) for step in self.recipe.recipe_instructions or []]),
            "notes": "\n\n".join([self.join_title_text(note) for note in self.recipe.notes or []]),
        }
        system_prompt = template.render(model_params)
        return {"role": "system", "content": json.dumps(system_prompt)}

    @staticmethod
    def join_title_text(element):
        header = ""
        if element.title is not None and element.title != "":
            header = element.title + "\n"
        return header + element.text

    async def ask_question(self, question: str) -> str | None:
        question_obj = {"role": "user", "content": question}
        message_chain = itertools.chain([self.build_prompt()], self.message_history, [question_obj])
        response = await self.messaging_service.send_question(message_chain)
        if response is None:
            return None
        self.message_history.append(question_obj)
        self.message_history.append(response.to_dict())
        return response.content
