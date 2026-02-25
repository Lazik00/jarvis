import asyncio
import logging
import platform
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger("jarvis.voice_output")


class VoiceOutputService:
    def __init__(self, piper_binary: str = "piper", voice_model: str = "models/en_US-lessac-medium.onnx") -> None:
        self.piper_binary = piper_binary
        self.voice_model = Path(voice_model)

    async def speak(self, text: str) -> None:
        if not text:
            return
        if shutil.which(self.piper_binary) and self.voice_model.exists():
            await asyncio.to_thread(self._speak_piper, text)
            return
        logger.warning("Piper not available. Falling back to console output.")
        print(f"Jarvis: {text}")

    def _speak_piper(self, text: str) -> None:
        output_device = "default"
        command = [
            self.piper_binary,
            "--model",
            str(self.voice_model),
            "--output-raw",
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=text.encode("utf-8"), timeout=30)
        if process.returncode != 0:
            raise RuntimeError(f"Piper failed: {stderr.decode('utf-8', errors='ignore')}")

        if platform.system().lower().startswith("win"):
            # Raw playback on Windows is not universal; keep text fallback for reliability.
            print(f"Jarvis: {text}")
            return

        play_cmd = shutil.which("aplay")
        if play_cmd:
            subprocess.run([play_cmd, "-r", "22050", "-f", "S16_LE", "-t", "raw"], input=stdout, check=False)
        else:
            logger.info("No audio player found for raw output. Text fallback used.")
            print(f"Jarvis: {text}")
