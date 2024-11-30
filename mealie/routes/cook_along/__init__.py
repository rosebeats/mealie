from fastapi import APIRouter

from . import cook_along

router = APIRouter()
router.include_router(cook_along.router)
