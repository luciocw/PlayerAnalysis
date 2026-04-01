# PlayerAnalysis

Análise de vídeo de futsal: filma com o celular, faz upload, e veja distância percorrida, velocidade, heatmap e arrancadas do jogador num dashboard interativo.

## Como funciona

```
Filma o jogo → Upload no browser → Clica os 4 cantos da quadra
→ Seleciona o jogador → Aguarda processamento → Dashboard + PDF
```

## Estrutura

```
apps/
  api/        Backend Python (FastAPI + YOLOv8 + processamento de vídeo)
  web/        Frontend Next.js (dashboard no browser)
scripts/      Scripts de setup e start
```

## Setup (uma vez só)

> Todos os comandos abaixo partem da pasta raiz do projeto.
> Clone o repositório e entre nela primeiro:
>
> ```bash
> git clone https://github.com/luciocw/PlayerAnalysis.git
> cd PlayerAnalysis
> ```

### 1. Backend

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install torch torchvision
pip install -r requirements.txt
cd ../..
```

### 2. Frontend

```bash
cd apps/web
npm install
cd ../..
```

### 3. Configurar o endereço do backend

```bash
cd apps/web
cp .env.example .env.local
# Edite .env.local e coloque o IP do seu Mac na rede local:
# NEXT_PUBLIC_API_URL=http://192.168.x.x:8000
cd ../..
```

Para saber o IP do seu Mac: `ipconfig getifaddr en0`

## Rodar

Abra **dois terminais**, ambos na raiz do projeto (`PlayerAnalysis/`).

**Terminal 1 — Backend:**
```bash
bash scripts/start-backend.sh
```

**Terminal 2 — Frontend:**
```bash
cd apps/web
npm run dev
```

Abra `http://localhost:3000` no browser.

## Testar o pipeline (Fase 0)

Para confirmar que o YOLOv8 funciona no seu Mac antes de usar a interface:

```bash
cd apps/api
source .venv/bin/activate
python scripts/test_pipeline.py --video /caminho/completo/para/video.mp4
cd ../..
```

## Métricas calculadas

| Métrica | Descrição |
|---|---|
| Distância total | Metros percorridos durante o jogo |
| Velocidade média | km/h médio em campo |
| Velocidade máxima | Pico de velocidade registrado |
| Arrancadas | Momentos acima de 18 km/h por mais de 0.5s |
| Heatmap | Mapa de calor das posições na quadra |

## Requisitos

- Mac com Python 3.10+ e Node.js 18+
- Vídeo filmado com câmera fixa (quadra inteira visível)
- Dimensões da quadra conhecidas (padrão futsal: 40m × 20m)
