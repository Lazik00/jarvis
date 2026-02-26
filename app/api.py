import contextlib
import asyncio
import json
import logging
import shutil

import psutil
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger("jarvis.api")
router = APIRouter()


class PromptRequest(BaseModel):
    text: str


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask")
async def ask(req: PromptRequest, request: Request) -> dict[str, str]:
    runtime = request.app.state.runtime
    response = await runtime.process_text(req.text)
    return {"response": response}


async def docker_snapshot() -> list[dict[str, str]]:
    if not shutil.which("docker"):
        return []
    process = await asyncio.create_subprocess_exec(
        "docker",
        "ps",
        "--format",
        "{{.Names}}|{{.Status}}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate()
    if process.returncode != 0:
        return []

    containers = []
    for row in stdout.decode("utf-8", errors="ignore").splitlines():
        if "|" not in row:
            continue
        name, status = row.split("|", 1)
        containers.append({"name": name.strip(), "status": status.strip()})
    return containers


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    runtime = ws.app.state.runtime
    await ws.send_json({"type": "ready", "message": "Jarvis online"})

    async def stats_loop() -> None:
        while True:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            containers = await docker_snapshot()
            await ws.send_json(
                {
                    "type": "system_stats",
                    "cpu": cpu,
                    "ram": ram,
                    "docker": "online" if containers else "unknown",
                }
            )
            await ws.send_json({"type": "docker_update", "containers": containers})
            await asyncio.sleep(5)

    stats_task = asyncio.create_task(stats_loop())

    try:
        while True:
            payload = await ws.receive_text()
            data = json.loads(payload)
            text = data.get("text", "").strip()
            if not text:
                await ws.send_json({"type": "error", "message": "Empty text"})
                continue
            await ws.send_json({"type": "jarvis_listening", "transcript": text})
            await ws.send_json({"type": "jarvis_thinking", "text": text})
            response = await runtime.process_text(text)
            await ws.send_json({"type": "jarvis_reply", "text": response, "stream": False})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Websocket failure: %s", exc)
        await ws.close(code=1011)
    finally:
        stats_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await stats_task
