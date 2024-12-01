from functools import cached_property

from mealie.services._base_service import BaseService
from mealie.services.cook_along import CookAlongMessagingService, CookAlongService
from mealie.services.recipe.recipe_service import RecipeService


class CookAlongManager(BaseService):
    """Manages CookAlongService instances, which track message history for a recipe"""

    cook_along_services: dict[str, CookAlongService] = {}
    """CookAlongService instances per recipe"""
    recipe_service: RecipeService
    """The recipe service for getting recipes"""

    @cached_property
    def messaging_service(self) -> CookAlongMessagingService:
        """Messaging service to communicate with OpenAI"""
        return CookAlongMessagingService()

    def __init__(self, recipe_service: RecipeService):
        """Stores the recipe service during initiation"""
        self.recipe_service = recipe_service
        super().__init__()

    def try_get_service(self, slug: str) -> CookAlongService | None:
        """Try to get a CookAlongService for a recipe slug. Returns None if one doesn't exist."""
        return self.cook_along_services.get(slug)

    def get_or_create_service(self, slug: str) -> CookAlongService:
        """
        Get a CookAlongService for a recipe slug. Creates one if it doesn't exist.
        Throws an error if the recipe doesn't exist
        """
        if slug not in self.cook_along_services:
            self.cook_along_services[slug] = CookAlongService(self.recipe_service.get_one(slug), self.messaging_service)
        return self.cook_along_services[slug]
