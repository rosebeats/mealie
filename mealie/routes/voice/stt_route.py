from functools import cached_property

from fastapi import UploadFile

from mealie.routes._base import BasePublicController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.voice.utilities import raise_connection_error
from mealie.schema.response import SuccessResponse
from mealie.services.voice_services import STTService

router = UserAPIRouter(prefix="/stt", tags=["Utils: Speech to Text"])


@controller(router)
class STTController(BasePublicController):
    @cached_property
    def service(self) -> STTService:
        return STTService()

    @router.post("", response_model=SuccessResponse)
    async def speech_to_text(self, audio: UploadFile):
        try:
            async with self.service as service:
                message = await service.transcribe(audio)
        except ConnectionError as exc:
            raise_connection_error(exc)
        return SuccessResponse(message=message)
