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
    """
    A service for assisting a user with following a recipe while cooking.
    We pass the OpenAI model a system prompt explaining its role and information about then recipe.
    Then we pass questions from the user about the recipe and get responses from the model.
    """

    message_history: list[ChatCompletionMessageParam] = []
    """The message history. Alternates between user and assistant messages. Does not include system prompt."""
    messaging_service: CookAlongMessagingService
    """The service for communicating with OpenAI"""
    recipe: Recipe
    """The recipe we're working from"""

    def __init__(self, recipe: Recipe, messaging_service: CookAlongMessagingService) -> None:
        """
        Initialize the service. This service is specific to a recipe.
        The messaging service lets us communicate with OpenAI.
        """
        self.messaging_service = messaging_service
        self.recipe = recipe
        super().__init__()

    def build_prompt(self) -> ChatCompletionMessageParam:
        """
        Builds a system prompt from the recipe. The prompt is passed:
            description: The recipe description
            ingredients: Each ingredient in the recipe
            instructions: All of the instructions from the recipe
            notes: All of the notes from the recipe
        These parameters are combined into a prompt in jinja and returned as a chat completion message
        """
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
        """Helper function to combine an optional title with text below it"""
        header = ""
        if element.title is not None and element.title != "":
            header = element.title + "\n"
        return header + element.text

    async def ask_question(self, question: str) -> str | None:
        """
        Ask OpenAI a new question.
        Asks OpenAI the passed in question and returns the answer. Saves this to the message history.
        """
        question_obj = {"role": "user", "content": question}
        message_chain = itertools.chain([self.build_prompt()], self.message_history, [question_obj])
        response = await self.messaging_service.send_question(message_chain)
        if response is None:
            return None
        self.message_history.append(question_obj)
        self.message_history.append(response.to_dict())
        return response.content
