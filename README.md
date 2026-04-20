# SDD Tech Writer

Gerador de artigos técnicos com pipeline em 4 etapas:
1. pesquisa
2. análise
3. escrita
4. validação automática

Você informa ferramentas + contexto + perguntas, e o sistema gera um artigo em Markdown.

## O que este projeto faz

- Busca dados na web (DuckDuckGo + scraping)
- Estrutura análise técnica
- Escreve artigo com template consistente
- Reprova automaticamente artigo ruim e tenta corrigir (até 5 iterações)
- Quando faltar evidência no critic, reexecuta pesquisa + análise antes de reescrever
- Usa fallback automático de LLM (OpenRouter -> Ollama Cloud -> Ollama Local)
- Reaproveita resultados de busca com cache (TTL) entre execuções
- Salva saídas e métricas em disco

## Arquitetura rápida

- `skills/researcher.py`: pesquisa e extração
- `skills/analyst.py`: análise técnica
- `skills/writer.py`: geração do artigo
- `skills/critic.py`: validação
- `pipeline.py`: orquestração
- `spec/article_spec.yaml`: regras, validação e parâmetros de geração
- `.env`: seleção de provider e modelos em runtime

## Diagrama de arquitetura

```text
+------------------+        +----------------------+
|   main.py (CLI)  | -----> |     pipeline.py      |
+------------------+        +----------+-----------+
                                        |
                 +----------------------+----------------------+
                 |                      |                      |
                 v                      v                      v
      +------------------+   +------------------+   +------------------+
      | skills/researcher|   |  skills/analyst  |   |  skills/writer   |
      +--------+---------+   +------------------+   +------------------+
               |
               +--> tools/search_tool.py
               +--> tools/scraper_tool.py
                                        |
                                        v
                             +------------------+
                             |  skills/critic   |
                             +--------+---------+
                                      |
                                      v
                        +------------------------------+
                        | validators/spec_validator.py |
                        +------------------------------+

Dependências centrais:
  pipeline.py --> spec/article_spec.yaml
  pipeline.py --> memory/

Saídas:
  pipeline.py --> output/debug_research.md
  pipeline.py --> output/debug_analysis.md
  pipeline.py --> output/pipeline_events.jsonl
  pipeline.py --> artigos/*.md
```

## Diagrama de fluxo

```text
1) main.py coleta:
   - ferramentas
   - contexto
   - foco
   - perguntas

2) pipeline.py executa:
   [Researcher] -> [Analyst] -> [Writer] -> [Critic]
                                     ^           |
                                     |           |
                                     +-----------+
                           (se reprovado e ainda há iteração)

   Se a reprovação indicar falta de dados/evidência:
   [Critic] -> [Researcher refresh] -> [Analyst] -> [Writer] -> [Critic]
             (limitado por pipeline.max_research_enrichments)

3) Critic decide:
   - aprovado ............... salva artigo + métricas + eventos
   - reprovado (com iteração) volta para Writer com correções
   - limite atingido ........ salva melhor versão disponível

LLM fallback (para researcher/analyst/writer/critic):
   OpenRouter
      |
      +-- falha (429/timeout) --> Ollama Cloud (glm5.1:cloud)
                                       |
                                       +-- falha --> Ollama Local
```

## Modos de LLM suportados

- `openrouter_free`
- `ollama_local`
- `ollama_cloud`

A escolha é feita por `LLM_PROVIDER` no `.env`.

## Quickstart

### 1) Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

Opcional (melhora scraping em páginas JS):
- `playwright` + Chromium

### 2) Instalação

```bash
git clone <seu-repositorio>
cd sdd-ollama

uv venv --python 3.12
source .venv/bin/activate
uv sync
```

Se precisar de fallback JS no scraping:

```bash
uv add playwright
playwright install chromium
```

### 3) Configuração de LLM

Copie o exemplo:

```bash
cp .env.example .env
```

Preencha no mínimo:

```env
LLM_PROVIDER=openrouter_free

LLM_MODEL_RESEARCHER=z-ai/glm-4.5-air:free
LLM_MODEL_ANALYST=z-ai/glm-4.5-air:free
LLM_MODEL_WRITER=z-ai/glm-4.5-air:free
LLM_MODEL_CRITIC=z-ai/glm-4.5-air:free
```

Se usar `openrouter_free`, também precisa:

```env
OPENROUTER_API_KEY=sk-or-v1-sua-chave
```

Se usar `ollama_local`:

```env
LLM_PROVIDER=ollama_local
# opcional
# OLLAMA_LOCAL_BASE_URL=http://localhost:11434
```

E garanta que o Ollama esteja de pé:

```bash
ollama list
curl http://localhost:11434
```

Se usar `ollama_cloud`:

```env
LLM_PROVIDER=ollama_cloud
# opcional
# OLLAMA_CLOUD_BASE_URL=https://ollama.com
# OLLAMA_CLOUD_API_KEY=
```

## Como rodar

```bash
python main.py
```

O CLI pede:
- ferramentas
- contexto
- foco
- perguntas obrigatórias
- checklist manual

## Comandos rápidos (sem contexto prévio)

### Rodar pipeline (modo padrão)

```bash
python main.py
```

### Forçar nova pesquisa (ignorar cache de busca)

```bash
python main.py --refresh-search
```

### Observabilidade

```bash
# Ver eventos gerados na execução mais recente
python watch_events.py

# Ver só os últimos eventos
python watch_events.py --tail=30

# Acompanhar em tempo real
python watch_events.py --watch
```

### Qualidade local (ruff + testes)

```bash
# Lint focado em problemas reais (unused args/imports/vars)
uv run ruff check . --select ARG,F401,F841

# Suite completa
uv run pytest -q

# Gate único (lint + testes)
uv run ruff check . && uv run pytest -q
```

## Saídas geradas

- `artigos/*.md`: artigo final
- `output/debug_research.md`: dados de pesquisa
- `output/debug_analysis.md`: análise intermediária
- `output/metrics.json`: métricas por execução
- `.memory/*.json`: memória entre execuções

## Configuração: quem controla o quê

- `.env`:
  - provider em runtime (`LLM_PROVIDER`)
  - modelos por role (`LLM_MODEL_*`)
  - modelos de fallback opcionais (`LLM_MODEL_FALLBACK_CLOUD`, `LLM_MODEL_FALLBACK_LOCAL`)
- `spec/article_spec.yaml`:
  - regras de qualidade
  - seções obrigatórias
  - timeout/temperature/context_length
  - timeout global da execução (`pipeline.timeout_total_seconds`)
  - enriquecimento de pesquisa pós-critic (`pipeline.max_research_enrichments`)
  - cache de busca (`research.search_cache.*`)

## Limitações conhecidas

- OpenRouter free pode limitar requisições (429 em pico)
- Com 429/timeout, o sistema tenta fallback cloud/local; se ambos falharem, encerra com erro amigável
- Qualidade em `ollama_local` depende do modelo/hardware
- Scraping pode falhar em sites complexos (há fallback)
- Sem bons resultados de busca, o artigo fica mais raso

## Estrutura do projeto

```text
spec/        contrato e regras
skills/      etapas de geração
tools/       busca e scraping
validators/  validação determinística
memory/      persistência de memória
output/      artefatos de execução
artigos/     artigos finais
```

## Próximos passos recomendados

1. Testar com `openrouter_free` para validar fluxo fim a fim
2. Trocar para `ollama_local` quando quiser custo zero recorrente
3. Ajustar `LLM_MODEL_*` por role para qualidade/velocidade

## Testes

```bash
# Suite completa
uv run pytest -q

# Suite específica
uv run pytest tests/test_pipeline_e2e.py -v
uv run pytest tests/test_spec_validator.py -v

# Cobertura
uv run pytest --cov=validators --cov=skills --cov=pipeline tests/ --cov-report=term-missing
```

Atualmente o projeto está com **142 testes passando**.

### Spec Versioning

This project uses semantic versioning for the spec:

```bash
# View current version
head -20 spec/article_spec.yaml

# Expected format: major.minor.patch (e.g., 1.0.0)
# Changes are tracked in spec_changelog section
```

See `docs/spec-implementation-mapping.md` for complete rule-to-code mapping.

## AWS local com MiniStack

O repositório inclui uma infra opcional para simular AWS localmente em `http://localhost:4566` com MiniStack.

Essa camada não substitui a pipeline principal e não é obrigatória para gerar artigos. O objetivo dela é oferecer um alvo de execução mais próximo de integrações reais com `AWS CLI`, `boto3` e Terraform, sem depender de uma conta AWS real.

### Quando usar

Use `host local` quando o fluxo for puramente local e não depender de APIs estilo AWS.

Use `aws emulada local (MiniStack)` quando você quiser:

- testar integrações com `S3`, `SQS`, `DynamoDB`, `STS` e serviços similares
- validar exemplos técnicos com endpoint real em `localhost:4566`
- reduzir diferença entre desenvolvimento local e ambiente que fala com APIs AWS
- resetar o estado do ambiente rapidamente entre testes

### O que você ganha

Comparado a um fluxo somente em `host local`, o ganho principal não é velocidade bruta da pipeline. O ganho é previsibilidade de integração.

- mesmo endpoint local para todo o time
- credenciais fake, sem risco de uso de conta AWS real
- ambiente resetável e reproduzível
- exemplos e testes mais próximos do comportamento esperado de SDKs AWS
- menos necessidade de mocks manuais para fluxos com bucket, fila e tabela

### O que não muda

- a pipeline continua sendo executada com `uv run python main.py`
- MiniStack continua opcional
- o uso de MiniStack pode adicionar algum overhead local de Docker; o benefício está na fidelidade do ambiente, não em poupar CPU/RAM

Arquivos principais:

- `docker-compose.ministack.yml`: modo base, ideal para desenvolvimento local do dia a dia
- `ministack/init-scripts/ready.d/01-bootstrap.py`: bootstrap automático do ambiente local
- `docs/ministack-local-aws.md`: guia de uso com AWS CLI, boto3 e Terraform

### O que o bootstrap faz

O arquivo `ministack/init-scripts/ready.d/01-bootstrap.py` existe para evitar que o MiniStack suba vazio. Sempre que o ambiente é iniciado, ele prepara um estado mínimo conhecido:

- cria o bucket `medium-sdd-local`
- cria a fila `medium-sdd-events`
- cria a tabela `medium-sdd-config`
- grava um objeto de healthcheck no bucket
- grava um item de bootstrap na tabela

Isso economiza setup manual e ajuda em testes repetíveis, principalmente quando você usa reset com reexecução de init scripts.

### Fluxo mínimo

1. Suba o MiniStack.

```bash
docker compose -f docker-compose.ministack.yml up -d
```

2. Verifique o healthcheck.

```bash
curl http://localhost:4566/_ministack/health
```

3. Se quiser validar a emulação, faça uma chamada AWS local.

```bash
aws --endpoint-url=http://localhost:4566 sts get-caller-identity
```

4. Rode a pipeline normalmente.

```bash
uv run python main.py
```

5. No CLI, escolha o alvo de execução `aws emulada local (MiniStack)` quando fizer sentido para o artigo ou cenário de integração.

### Reset do ambiente

Reset com reexecução dos scripts de init:

```bash
curl -X POST "http://localhost:4566/_ministack/reset?init=1"
```

Isso limpa o estado atual e recria os recursos básicos definidos no bootstrap.
