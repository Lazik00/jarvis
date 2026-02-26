import json
import logging
from typing import Any

import httpx

logger = logging.getLogger("jarvis.brain")

SYSTEM_PROMPT = """
You are Jarvis, a local voice assistant.
Return ONLY valid JSON with keys:
- intent: short intent name
- command: command plugin name (system|docker|devops|chat)
- action: action function name
- args: JSON object of parameters
- say: short spoken response

If request is not a system command, use command='chat', action='answer'.
Supported actions:
- system.open_application
- system.cpu_usage
- system.ram_usage
- system.disk_usage
- docker.status
- docker.logs
- devops.restart_service
- devops.check_logs
""".strip()


class BrainService:
    def __init__(self, model: str, ollama_base_url: str) -> None:
        self.model = model
        self.base_url = ollama_base_url.rstrip("/")

    async def parse_command(self, text: str, context: list[dict[str, str]]) -> dict[str, Any]:
        user_prompt = {
            "text": text,
            "context": context[-4:],
        }
        payload = {
            "model": self.model,
            "prompt": f"{SYSTEM_PROMPT}\n\nInput: {json.dumps(user_prompt)}",
            "stream": False,
            "format": "json",
        }
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
            raw = response.json().get("response", "{}")
            logger.info("LLM raw response: %s", raw)
            parsed = json.loads(raw)
            return {
                "intent": parsed.get("intent", "chat"),
                "command": parsed.get("command", "chat"),
                "action": parsed.get("action", "answer"),
                "args": parsed.get("args", {}),
                "say": parsed.get("say", "Okay."),
                "text": text,
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("LLM parse failed: %s", exc)
            return {
                "intent": "chat",
                "command": "chat",
                "action": "answer",
                "args": {"text": text},
                "say": "I could not parse that command, but I can still respond.",
                "text": text,
            }
