# Guia Completo — Como usar o PlayerAnalysis

> Para iniciantes. Sem precisar saber programar.

---

## O que você vai precisar

- Mac com o projeto já instalado (setup já foi feito)
- Um vídeo MP4 ou MOV filmado com o celular
- Terminal (o app "Terminal" do Mac)

---

## Parte 1 — Abrir o Terminal

1. Pressione **Command (⌘) + Espaço** para abrir o Spotlight
2. Digite **Terminal** e pressione Enter
3. Uma janela preta/escura vai abrir — é aqui que você digita os comandos

> **Dica:** Você vai precisar de **dois terminais abertos ao mesmo tempo**. Para abrir o segundo, pressione **Command (⌘) + T** dentro do Terminal.

---

## Parte 2 — Toda vez que for usar o sistema

### Terminal 1 — Iniciar o Backend (processamento de vídeo)

Digite os comandos **um por vez**, aguardando cada um terminar:

```
cd /Users/luciocw/Desktop/Foothub\ Scouting\ Análise\ de\ Mercado/Projeto\ Analise\ Futebol
```
```
bash scripts/start-backend.sh
```

Você vai ver algo assim — significa que está funcionando:
```
🚀  Iniciando backend em http://localhost:8000
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

> **Deixe este terminal aberto.** Não feche enquanto estiver usando o sistema.

---

### Terminal 2 — Iniciar o Dashboard (a tela que você vai usar)

Abra um segundo terminal (**Command + T**) e digite:

```
cd /Users/luciocw/Desktop/Foothub\ Scouting\ Análise\ de\ Mercado/Projeto\ Analise\ Futebol/apps/web
```
```
npm run dev
```

Você vai ver:
```
▲ Next.js 15.1.0
- Local:        http://localhost:3000
```

---

### Abrir no navegador

Abra o **Safari** ou **Chrome** e acesse:

```
http://localhost:3000
```

O dashboard vai aparecer.

---

## Parte 3 — Analisar um jogo

### Passo 1 — Nova Sessão

1. Clique em **"Nova Sessão"**
2. Informe as dimensões da quadra (padrão futsal: **40m de largura, 20m de altura**)
3. Arraste o vídeo para a área de upload, ou clique para selecionar
4. Aguarde o upload terminar (uma barra de progresso vai aparecer)

---

### Passo 2 — Calibrar a quadra

1. Uma imagem do primeiro frame do vídeo vai aparecer
2. Clique nos **4 cantos da quadra** nesta ordem:
   - Canto superior esquerdo
   - Canto superior direito
   - Canto inferior direito
   - Canto inferior esquerdo
3. Vai aparecer um marcador numerado em cada canto
4. Clique em **"Confirmar"**

> **Dica:** Quanto mais preciso você clicar nos cantos reais da quadra, mais precisas serão as métricas de distância e velocidade.
>
> **Esta calibração fica salva.** Para a mesma quadra, você não precisará repetir.

---

### Passo 3 — Identificar o jogador

1. Uma grade de fotos vai aparecer com os jogadores detectados no vídeo
2. Clique na foto do seu filho
3. Clique em **"Confirmar"**

---

### Passo 4 — Processar o vídeo

1. Clique em **"Iniciar Processamento"**
2. Uma barra de progresso vai mostrar o andamento
3. Também aparece:
   - Em qual etapa está ("Detectando jogadores...", "Calculando métricas...")
   - Tempo estimado para terminar
   - Quantos frames já foram analisados

> **Quanto tempo demora?**
> - Vídeo de 10 minutos: ~5 a 10 min
> - Vídeo de 40 minutos (jogo): ~20 a 40 min
> - Depende do seu Mac
>
> **Não feche o terminal nem coloque o Mac para dormir.**

---

### Passo 5 — Ver o Dashboard

Quando terminar, o dashboard vai aparecer automaticamente com:

| O que aparece | O que significa |
|---|---|
| **Distância Total** | Quantos metros o jogador correu no total |
| **Velocidade Média** | Média de km/h durante o jogo |
| **Velocidade Máxima** | O pico de velocidade registrado |
| **Arrancadas** | Quantas vezes passou de 18 km/h |
| **Mapa de Calor** | Onde o jogador ficou mais na quadra |
| **Gráfico de Velocidade** | Como a velocidade variou ao longo do jogo |

---

### Passo 6 — Exportar o PDF

1. Clique no botão **"Exportar PDF"**
2. O arquivo vai ser baixado automaticamente
3. Abra no Preview e imprima, ou mande por WhatsApp para o treinador

---

## Parte 4 — Ver análises anteriores

Na tela inicial, todas as sessões ficam salvas com:
- Nome do vídeo
- Data da análise
- Status (processando, concluído, etc.)

Clique em qualquer sessão para ver o dashboard novamente.

---

## Parte 5 — Parar o sistema

Quando terminar de usar:

1. No **Terminal 2** (frontend): pressione **Control + C**
2. No **Terminal 1** (backend): pressione **Control + C**

Pode fechar os terminais depois.

---

## Dicas para filmar bem

Para ter métricas mais precisas:

- **Câmera fixa** — apoie o celular em algum lugar estável (arquibancada, janela, tripé)
- **Quadra inteira visível** — quanto mais da quadra aparecer, melhor
- **Câmera alta e de lado** — evite filmar de frente ou de um ângulo muito inclinado
- **Boa iluminação** — luz boa ajuda o sistema a detectar os jogadores
- **Qualidade** — filme em HD (1080p), que o celular já faz automaticamente

---

## Problemas comuns

### "Não consigo acessar http://localhost:3000"
→ O Terminal 2 (frontend) não está rodando. Execute `npm run dev` novamente.

### "O backend não responde"
→ O Terminal 1 (backend) não está rodando. Execute `bash scripts/start-backend.sh` novamente.

### "O jogador não aparece na grade de fotos"
→ O vídeo pode estar muito escuro ou o jogador pode estar fora do frame nos primeiros 10 segundos. Tente um vídeo com melhor iluminação.

### "As métricas de distância parecem erradas"
→ Refaça a calibração clicando com mais precisão nos cantos da quadra.

### O Mac desligou durante o processamento
→ Abra o sistema normalmente e processe o vídeo novamente. Próxima vez, deixe o Mac conectado na tomada e vá em **Configurações → Bateria → desligar "Colocar disco em repouso quando possível"**.

---

## Atalhos úteis no Terminal

| Atalho | O que faz |
|---|---|
| **Control + C** | Para o que está rodando |
| **Command + T** | Abre nova aba no Terminal |
| **Seta para cima ↑** | Repete o último comando digitado |
