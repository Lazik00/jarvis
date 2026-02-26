# Jarvis Docker Setup

```bash
cp docker/.env.example docker/.env
cd docker
docker compose up -d --build
```

## Services

- Backend: http://localhost:8000/health
- UI: http://localhost:5173
- WebSocket: ws://localhost:8000/ws

## Logs

```bash
cd docker
docker compose logs -f jarvis-backend
docker compose logs -f jarvis-ui
docker compose logs -f ollama
```

## Stop

```bash
cd docker
docker compose down
```
