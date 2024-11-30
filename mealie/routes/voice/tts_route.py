import os
from functools import cached_property

from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from mealie.routes._base import BasePublicController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.services.voice_services import TTSService

router = UserAPIRouter(prefix="/tts", tags=["Utils: Text to Speech"])


@controller(router)
class TTSController(BasePublicController):
    @cached_property
    def service(self) -> TTSService:
        return TTSService()

    @router.post("")
    async def text_to_speech(self, text: str):
        async with self.service as service:
            filename = await service.synthesize(text)
        return FileResponse(filename, media_type="audio/wav", background=BackgroundTask(os.remove, filename))
