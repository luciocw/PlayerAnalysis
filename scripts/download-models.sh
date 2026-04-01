#!/bin/bash
# Baixa os pesos do YOLOv8n (modelo de detecção)
# Só precisa rodar uma vez

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/../apps/api/models"

mkdir -p "$MODELS_DIR"

if [ -f "$MODELS_DIR/yolov8n.pt" ]; then
  echo "✓  yolov8n.pt já existe em apps/api/models/"
  exit 0
fi

echo "📥  Baixando yolov8n.pt (~6 MB)..."

# O ultralytics baixa automaticamente na primeira vez que o modelo é carregado.
# Este script apenas aciona esse download de forma explícita.
cd "$SCRIPT_DIR/../apps/api"
source .venv/bin/activate
python3 -c "
from ultralytics import YOLO
import shutil, os
model = YOLO('yolov8n.pt')  # baixa para ~/.cache/ultralytics
# Copia para o diretório de modelos do projeto
cache_path = os.path.expanduser('~/.cache/ultralytics/yolov8n.pt')
if os.path.exists(cache_path):
    shutil.copy(cache_path, 'models/yolov8n.pt')
    print('✓  yolov8n.pt copiado para apps/api/models/')
else:
    print('✓  yolov8n.pt disponível no cache do ultralytics')
"
