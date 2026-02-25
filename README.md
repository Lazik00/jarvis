# Jarvis (Local Offline Assistant)

## Project Tree

```text
jarvis/
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── brain.py
│   ├── main.py
│   ├── memory.py
│   ├── router.py
│   ├── voice_input.py
│   ├── voice_output.py
│   └── commands/
│       ├── __init__.py
│       ├── devops.py
│       ├── docker.py
│       └── system.py
├── data/
├── models/
├── requirements.txt
├── run.sh
└── README.md
```

## Features

- Wake word: `Jarvis`
- Voice flow: Mic → Whisper → Ollama LLM → Command Router → Action → Piper TTS
- FastAPI WebSocket for real-time interaction
- SQLite memory with optional ChromaDB vector retrieval
- DevOps actions: docker compose status, docker logs, service restart, logs, CPU/RAM/Disk monitoring

## Ubuntu Setup

### 1) System dependencies

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip ffmpeg portaudio19-dev aplay curl
```

### 2) Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull mistral
```

### 3) Install Piper TTS

```bash
mkdir -p models
cd models
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
cd ..
```

Install Piper binary (one option):

```bash
pip install piper-tts
```

### 4) Python environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5) Run Jarvis

```bash
./run.sh
```

## Windows Setup

### 1) Install prerequisites

- Python 3.11+
- Git
- FFmpeg (add to PATH)
- Ollama for Windows

### 2) Install and pull model

```powershell
ollama serve
ollama pull mistral
```

### 3) Install Piper + model

```powershell
mkdir models
# Download files into models/:
# en_US-lessac-medium.onnx
# en_US-lessac-medium.onnx.json
pip install piper-tts
```

### 4) Python environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
set PYTHONPATH=%cd%
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Usage

### Health

```bash
curl http://localhost:8000/health
```

### Ask (text)

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"text":"show cpu usage"}'
```

### WebSocket

- Endpoint: `ws://localhost:8000/ws`
- Request frame:

```json
{"text":"docker status"}
```

## Example commands

- `Jarvis open vscode`
- `Jarvis docker status`
- `Jarvis show cpu usage`
- `Jarvis restart nginx`
- `Jarvis check logs nginx`

## Notes

- For Uzbek voice, swap Piper model with Uzbek-supported voice and update `voice_model` path in `app/main.py`.
- For fully local operation, ensure Ollama, Piper model, and Whisper model are pre-downloaded.

## Desktop UI (Electron + React + Tailwind)

```text
jarvis-ui/
├── electron/
│   └── main.cjs
├── src/
│   ├── components/
│   │   ├── ChatPanel.tsx
│   │   ├── DevOpsPanel.tsx
│   │   ├── LogViewer.tsx
│   │   ├── Sidebar.tsx
│   │   └── VoiceIndicator.tsx
│   ├── hooks/
│   │   ├── useJarvisState.ts
│   │   └── useSocket.ts
│   ├── pages/
│   │   └── Home.tsx
│   ├── styles/
│   │   └── globals.css
│   └── main.tsx
├── index.html
├── package.json
├── postcss.config.cjs
├── tailwind.config.ts
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

### Start UI

```bash
cd jarvis-ui
npm install
npm run dev
```
