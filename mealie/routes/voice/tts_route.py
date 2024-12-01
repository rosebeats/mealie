import os
from functools import cached_property

from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from mealie.routes._base import BasePublicController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.voice.utilities import raise_connection_error
from mealie.services.voice_services import TTSService

router = UserAPIRouter(prefix="/tts", tags=["Utils: Text to Speech"])


@controller(router)
class TTSController(BasePublicController):
    """Controller for text to speech API"""

    @cached_property
    def service(self) -> TTSService:
        """The text to speech service"""
        return TTSService()

    @router.post("")
    async def text_to_speech(self, text: str):
        """Convert passed in text into speech"""
        try:
            async with self.service as service:
                filename = await service.synthesize(text)
        except ConnectionError as exc:
            raise_connection_error(exc)
        return FileResponse(filename, media_type="audio/wav", background=BackgroundTask(os.remove, filename))
