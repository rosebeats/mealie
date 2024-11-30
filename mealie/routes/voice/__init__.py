from fastapi import APIRouter

from mealie.routes.voice import stt_route, tts_route

router = APIRouter(prefix="/voice")
router.include_router(stt_route.router)
router.include_router(tts_route.router)
