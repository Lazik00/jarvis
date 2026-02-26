#!/usr/bin/env sh
set -eu

OLLAMA_BASE_URL="${OLLAMA_HOST:-http://ollama:11434}"
MODEL="${JARVIS_MODEL:-mistral}"

until curl -fsS "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; do
  echo "Waiting for Ollama at ${OLLAMA_BASE_URL}..."
  sleep 2
done

echo "Pulling model: ${MODEL}"
ollama pull "${MODEL}"
echo "Model ready: ${MODEL}"
