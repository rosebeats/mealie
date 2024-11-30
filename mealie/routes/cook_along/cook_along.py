from functools import cached_property

from fastapi import APIRouter

from mealie.routes._base import BaseUserController, controller
from mealie.schema.cook_along import CookAlongQuestion
from mealie.schema.response.responses import SuccessResponse
from mealie.services.cook_along import CookAlongManager
from mealie.services.recipe.recipe_service import RecipeService

router = APIRouter(prefix="/cookalong", tags=["Recipe: Cook Along"])


@controller(router)
class CookAlongController(BaseUserController):
    @cached_property
    def manager(self) -> CookAlongManager:
        recipe_service = RecipeService(self.repos, self.user, self.household, translator=self.translator)
        return CookAlongManager(recipe_service)

    @router.post("/{slug}", response_model=SuccessResponse)
    async def cook_along(self, slug: str, question: CookAlongQuestion):
        service = self.manager.get_cook_along_service(slug)
        return SuccessResponse(message=await service.ask_question(question.question))
