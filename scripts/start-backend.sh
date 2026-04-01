#!/bin/bash
# Inicia o backend FastAPI e mantém o Mac acordado durante o processamento

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$SCRIPT_DIR/../apps/api"

cd "$API_DIR"

if [ ! -d ".venv" ]; then
  echo "❌  Ambiente virtual não encontrado. Rode primeiro: cd apps/api && python3 -m venv .venv && pip install -r requirements.txt"
  exit 1
fi

source .venv/bin/activate

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️  Arquivo .env criado a partir do .env.example. Verifique as configurações."
fi

echo "🚀  Iniciando backend em http://localhost:8000"
echo "   (Mac não vai dormir enquanto o servidor estiver rodando)"
echo "   Pressione Ctrl+C para parar."
echo ""

# caffeinate impede o Mac de dormir durante processamento de vídeo
caffeinate -i uvicorn main:app --host 0.0.0.0 --port 8000 --reload
