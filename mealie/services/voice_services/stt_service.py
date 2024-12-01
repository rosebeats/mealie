import wave

from fastapi import UploadFile
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import wav_to_chunks
from wyoming.client import AsyncClient

from mealie.services._base_service import BaseService

SAMPLES_PER_CHUNK = 1024


class STTService(BaseService):
    """A service for performing speech to text conversion"""

    client: AsyncClient
    """The wyoming protocol client providing speech to text"""
    connected: bool = False
    """Whether the client is connected"""

    def __init__(self):
        """Initialize the speech to text client"""
        super().__init__()
        self.client = AsyncClient.from_uri(self.settings.SPEECH_TO_TEXT_URI)

    async def __aenter__(self):
        """Set up a connection asyncronously"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Set up a connection asyncronously"""
        await self.disconnect()

    async def connect(self):
        """Set up a connection asyncronously"""
        if self.connected:
            return
        await self.client.connect()
        self.connected = True

    async def disconnect(self):
        """Destroy the connection asyncronously"""
        if not self.connected:
            return
        await self.client.disconnect()
        self.connected = False

    async def transcribe(self, audio: UploadFile) -> str | None:
        """Transcribe an uploaded audio file to text"""
        transcribe_event = Transcribe(self.settings.SPEECH_TO_TEXT_MODEL, self.settings.SPEECH_TO_TEXT_LANGUAGE)
        await self.client.write_event(transcribe_event.event())
        with wave.open(audio.file, "rb") as audio_file:
            audio_events = wav_to_chunks(audio_file, SAMPLES_PER_CHUNK, start_event=True, stop_event=True)
            for audio_event in audio_events:
                await self.client.write_event(audio_event.event())
        transcript: Transcript = Transcript.from_event(await self.client.read_event())
        return transcript.text
