from functools import cached_property

from fastapi import APIRouter, HTTPException

from mealie.core import exceptions
from mealie.routes._base import BaseUserController, controller
from mealie.schema.cook_along import AIAssistantMessage, AIUserMessage, open_ai_to_message
from mealie.services.cook_along import CookAlongManager
from mealie.services.recipe.recipe_service import RecipeService

router = APIRouter(prefix="/cookalong", tags=["Recipe: Cook Along"])


@controller(router)
class CookAlongController(BaseUserController):
    @cached_property
    def manager(self) -> CookAlongManager:
        recipe_service = RecipeService(self.repos, self.user, self.household, translator=self.translator)
        return CookAlongManager(recipe_service)

    @router.post("/{slug}", response_model=AIAssistantMessage)
    async def cook_along(self, slug: str, question: AIUserMessage):
        try:
            service = self.manager.get_or_create_service(slug)
        except exceptions.NoEntryFound as exc:
            raise HTTPException(status_code=404, detail="recipe does not exist") from exc
        return AIAssistantMessage(content=await service.ask_question(question.content))

    @router.get("/{slug}", response_model=list[AIAssistantMessage | AIUserMessage])
    async def get_message_history(self, slug: str):
        service = self.manager.try_get_service(slug)
        if service is None or len(service.message_history) == 0:
            raise HTTPException(status_code=404, detail="no message history for this recipe")
        return [open_ai_to_message(message) for message in service.message_history]

    @router.delete("/{slug}", status_code=204)
    async def delete_history(self, slug: str):
        service = self.manager.try_get_service(slug)
        if service is None:
            raise HTTPException(status_code=404, detail="no message history for this recipe")
        service.message_history = []
