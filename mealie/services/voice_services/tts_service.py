import tempfile
import wave

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.client import AsyncClient
from wyoming.tts import Synthesize, SynthesizeVoice

from mealie.services._base_service import BaseService


class TTSService(BaseService):
    client: AsyncClient
    connected: bool = False

    def __init__(self):
        super().__init__()
        self.client = AsyncClient.from_uri(self.settings.TEXT_TO_SPEECH_URI)
        self.voice = SynthesizeVoice(self.settings.TEXT_TO_SPEECH_VOICE)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

    async def connect(self):
        if self.connected:
            return
        await self.client.connect()
        self.connected = True

    async def disconnect(self):
        if not self.connected:
            return
        await self.client.disconnect()
        self.connected = False

    async def synthesize(self, text: str) -> str:
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
