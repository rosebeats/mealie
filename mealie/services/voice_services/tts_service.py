import tempfile
import wave

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.client import AsyncClient
from wyoming.tts import Synthesize, SynthesizeVoice

from mealie.services._base_service import BaseService


class TTSService(BaseService):
    """A service for performing text to speech conversion"""

    client: AsyncClient
    """The wyoming protocol client providing text to speech"""
    connected: bool = False
    """Whether the client is connected"""
    voice: SynthesizeVoice
    """The voice to use for synthesizing speech"""

    def __init__(self):
        """Initialize the text to speech client and voice"""
        super().__init__()
        self.client = AsyncClient.from_uri(self.settings.TEXT_TO_SPEECH_URI)
        self.voice = SynthesizeVoice(self.settings.TEXT_TO_SPEECH_VOICE)

    async def __aenter__(self):
        """Set up a connection asyncronously"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Destroy the connection asyncronously"""
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

    async def synthesize(self, text: str) -> str:
        """
        Synthesize speech from text. Returns the filename of a temporary file.
        Caller is responsible for cleaning file up.
        """
        synthesize_event = Synthesize(text, self.voice)
        await self.client.write_event(synthesize_event.event())
        wave_file = tempfile.NamedTemporaryFile("wb", delete=False)
        try:
            wave_writer: wave.Wave_write = wave.open(wave_file, "wb")
            audio_start = AudioStart.from_event(await self.client.read_event())
            wave_writer.setframerate(audio_start.rate)
            wave_writer.setsampwidth(audio_start.width)
            wave_writer.setnchannels(audio_start.channels)
            while True:
                event = await self.client.read_event()
                if AudioStop.is_type(event.type):
                    break
                audio_chunk = AudioChunk.from_event(event)
                wave_writer.writeframes(audio_chunk.audio)
        finally:
            wave_writer.close()
        return wave_file.name
