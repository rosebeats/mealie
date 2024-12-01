from functools import cached_property

from mealie.services._base_service import BaseService
from mealie.services.cook_along import CookAlongMessagingService, CookAlongService
from mealie.services.recipe.recipe_service import RecipeService


class CookAlongManager(BaseService):
    cook_along_services: dict[str, CookAlongService] = {}
    recipe_service: RecipeService

    @cached_property
    def messaging_service(self) -> CookAlongMessagingService:
        return CookAlongMessagingService()

    def __init__(self, recipe_service: RecipeService):
        self.recipe_service = recipe_service
        super().__init__()

    def try_get_service(self, slug: str) -> CookAlongService | None:
        return self.cook_along_services.get(slug)

    def get_or_create_service(self, slug: str) -> CookAlongService:
        if slug not in self.cook_along_services:
            self.cook_along_services[slug] = CookAlongService(self.recipe_service.get_one(slug), self.messaging_service)
        return self.cook_along_services[slug]
