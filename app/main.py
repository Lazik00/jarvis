import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as api_router
from app.memory import MemoryStore
from app.router import CommandRouter
from app.voice_input import VoiceInputService
from app.voice_output import VoiceOutputService
from app.brain import BrainService

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("jarvis.main")


class JarvisRuntime:
    def __init__(self) -> None:
        self.memory = MemoryStore(db_path="data/jarvis.db")
        self.voice_output = VoiceOutputService(piper_binary="piper", voice_model="models/en_US-lessac-medium.onnx")
        self.brain = BrainService(model="mistral", ollama_base_url="http://localhost:11434")
        self.router = CommandRouter()
        self.voice_input = VoiceInputService(model_size="base", wake_word="jarvis")
        self.task: asyncio.Task | None = None
        self.running = False

    async def startup(self) -> None:
        logger.info("Starting Jarvis runtime")
        await self.memory.initialize()
        await self.router.initialize()
        self.running = True
        self.task = asyncio.create_task(self.background_voice_loop())

    async def shutdown(self) -> None:
        logger.info("Shutting down Jarvis runtime")
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        await self.memory.close()

    async def process_text(self, text: str) -> str:
        try:
            await self.memory.save_message(role="user", content=text)
            context = await self.memory.recent_messages(limit=10)
            llm_result = await self.brain.parse_command(text=text, context=context)
            result = await self.router.dispatch(llm_result)
            final_text = result.get("message") or llm_result.get("say") or "Done."
            await self.memory.save_message(role="assistant", content=final_text)
            await self.voice_output.speak(final_text)
            return final_text
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to process text: %s", exc)
            error_text = f"I hit an error: {exc}"
            await self.memory.save_message(role="assistant", content=error_text)
            return error_text

    async def background_voice_loop(self) -> None:
        while self.running:
            try:
                text = await self.voice_input.capture_once()
                if not text:
                    continue
                if self.voice_input.is_wake_command(text):
                    await self.voice_output.speak("Yes, I am listening.")
                    follow_up = await self.voice_input.capture_once(timeout=8)
                    if follow_up:
                        await self.process_text(follow_up)
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("Voice loop error: %s", exc)
                await asyncio.sleep(1)


runtime = JarvisRuntime()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await runtime.startup()
    try:
        yield
    finally:
        await runtime.shutdown()


app = FastAPI(title="Jarvis Local Assistant", version="1.0.0", lifespan=lifespan)
app.include_router(api_router)
app.state.runtime = runtime
