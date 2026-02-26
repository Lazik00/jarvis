import asyncio
import logging
import tempfile
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

logger = logging.getLogger("jarvis.voice_input")


class VoiceInputService:
    def __init__(self, model_size: str = "base", wake_word: str = "jarvis", sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate
        self.wake_word = wake_word.lower()
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    async def capture_once(self, seconds: int = 5, timeout: int = 6) -> str:
        return await asyncio.wait_for(asyncio.to_thread(self._record_and_transcribe, seconds), timeout=timeout)

    def _record_and_transcribe(self, seconds: int) -> str:
        logger.debug("Recording for %s seconds", seconds)
        recording = sd.rec(int(seconds * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype="int16")
        sd.wait()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = Path(tmp.name)
        self._write_wav(wav_path, recording)
        try:
            segments, _ = self.model.transcribe(str(wav_path), language="en")
            text = " ".join(segment.text.strip() for segment in segments).strip()
            logger.info("Transcribed: %s", text)
            return text
        finally:
            wav_path.unlink(missing_ok=True)

    def _write_wav(self, path: Path, audio: np.ndarray) -> None:
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio.tobytes())

    def is_wake_command(self, text: str) -> bool:
        return self.wake_word in text.lower().strip()
