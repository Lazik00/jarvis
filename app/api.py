import asyncio
import json
import logging

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


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    runtime = ws.app.state.runtime
    await ws.send_json({"type": "ready", "message": "Jarvis online"})
    try:
        while True:
            payload = await ws.receive_text()
            data = json.loads(payload)
            text = data.get("text", "").strip()
            if not text:
                await ws.send_json({"type": "error", "message": "Empty text"})
                continue
            await ws.send_json({"type": "processing", "text": text})
            response = await runtime.process_text(text)
            await ws.send_json({"type": "response", "text": response})
            await asyncio.sleep(0)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Websocket failure: %s", exc)
        await ws.close(code=1011)
