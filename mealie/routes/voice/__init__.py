from fastapi import APIRouter

from mealie.routes.voice import stt_route

router = APIRouter(prefix="/voice")
router.include_router(stt_route.router)
