import itertools

from openai.resources.chat.completions import ChatCompletionMessageParam

from mealie.schema.recipe.recipe import Recipe
from mealie.services._base_service import BaseService
from mealie.services.cook_along import CookAlongMessagingService


class CookAlongService(BaseService):
    message_history: list[ChatCompletionMessageParam] = []
    messaging_service: CookAlongMessagingService
    recipe: Recipe

    def __init__(self, recipe: Recipe, messaging_service: CookAlongMessagingService) -> None:
        self.messaging_service = messaging_service
        self.recipe = recipe
        super().__init__()

    def build_prompt(self) -> ChatCompletionMessageParam:
        return {"role": "system", "content": "The user will ask a question of you. Please just answer the question."}

    async def ask_question(self, question: str) -> str | None:
        question_obj = {"role": "user", "content": question}
        message_chain = itertools.chain([self.build_prompt()], self.message_history, [question_obj])
        response = await self.messaging_service.send_question(message_chain)
        if response is None:
            return None
        self.message_history.append(question_obj)
        self.message_history.append(response)
        return response.content
