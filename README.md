# SDD Tech Writer

Gerador de artigos técnicos comparativos usando LLMs locais via Ollama.

Você informa as ferramentas, o contexto de uso e as perguntas que o artigo deve responder. O sistema pesquisa (via DuckDuckGo), analisa, escreve e valida. Tudo roda na sua máquina sem enviar dados para APIs pagas ou depender de chaves externas.

---

## Por que SDD

SDD (Spec-Driven Development) é uma abordagem onde a **especificação é a fonte de verdade**, não o código ou o texto gerado. Todo output deriva de um contrato formal definido antes da execução.

No desenvolvimento tradicional de conteúdo técnico, o que é um "bom artigo" vive na cabeça de quem escreve. Aqui, vive em `spec/article_spec.yaml`. Isso significa que:

- O modelo não decide o que é aceitável. A spec decide.
- A validação é determinística e não subjetiva.
- Quando a spec muda, o comportamento muda junto em todo o pipeline.

O resultado prático é que o sistema **rejeita outputs ruins automaticamente** e tenta corrigir antes de entregar.

---

## O que está sendo usado e por quê

### Spec (`spec/article_spec.yaml`)
Define o contrato do artigo: seções obrigatórias, regras de qualidade, modelos a usar e configuração do Ollama. É o único arquivo que você precisa editar para mudar o comportamento global do sistema.

### Skills
Cada etapa do pipeline é uma classe especializada com responsabilidade única. Modelos locais menores performam melhor em tarefas focadas do que em prompts gigantes que pedem tudo de uma vez.

| Skill | Responsabilidade |
|-------|-----------------|
| `ResearcherSkill` | Busca na web (DuckDuckGo) e extrai dados factuais |
| `AnalystSkill` | Transforma dados brutos em análise comparativa |
| `WriterSkill` | Monta o artigo seguindo a spec |
| `CriticSkill` | Valida o artigo em duas camadas |

### Critic em duas camadas
**Camada 1 (Determinística):** Verifica estrutura, placeholders, URLs e mínimos de qualidade. Sem LLM, sem custo de tokens, sempre confiável.

**Camada 2 (Semântica):** Pergunta ao modelo se há contradições internas ou números impossíveis. Só roda se a camada 1 passou.

Se o artigo reprovar, o pipeline tenta corrigir automaticamente (máximo 3 iterações) antes de salvar.

### Memory
O sistema aprende entre execuções. Quando uma correção resolve um problema recorrente, isso é salvo e injetado como contexto nas próximas execuções.

| Tipo | O que guarda |
|------|-------------|
| Working | Estado da sessão atual |
| Episódica | Log do que aconteceu (persistente) |
| Procedural | Receitas de correção que funcionaram |

### Observability
Cada etapa mostra spinner, tempo de execução e resultado em tempo real. Métricas de cada execução são salvas em `output/metrics.json` para análise posterior.

---

## Estrutura do projeto

```text
projeto/
├── spec/
│   └── article_spec.yaml      # contrato - edite aqui para mudar comportamento
├── memory/
│   └── memory_store.py        # memória persistente entre execuções
├── validators/
│   └── spec_validator.py      # validação determinística
├── skills/
│   ├── researcher.py          # busca e extração de dados
│   ├── analyst.py             # análise comparativa
│   ├── writer.py              # geração do artigo
│   └── critic.py              # validação em duas camadas
├── tools/
│   └── search_tool.py         # integração DuckDuckGo
├── logger.py                  # output visual com Rich
├── pipeline.py                # orquestração do fluxo
├── main.py                    # CLI interativo
├── .memory/                   # criado automaticamente
├── output/                    # criado automaticamente
└── artigos/                   # artigos gerados
```

---

## Instalação

### 1. Pré-requisitos

**Rust** (necessário para compilar dependências Python):
```bash
curl --proto '=https' --tlsv1.2 -sSf [https://sh.rustup.rs](https://sh.rustup.rs) | sh
source ~/.cargo/env
rustup default stable
```

**Ollama:**
```bash
# Linux
curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh

# Windows
# baixe em [https://ollama.com/download/windows](https://ollama.com/download/windows)
```

**uv** (gerenciador de pacotes):
```bash
# Linux/macOS
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
```

### 2. Clone e configure o projeto

```bash
git clone <seu-repositorio>
cd sdd-ollama

# cria ambiente virtual com Python 3.12
uv venv --python 3.12
uv add ollama requests python-dotenv pyyaml rich duckduckgo-search
```

### 3. Baixe os modelos

Atente-se ao limite de hardware. Modelos 14B exigem pelo menos 16GB de RAM. Se você possui 8GB de RAM, utilize apenas modelos 7B ou 8B.

```bash
ollama pull qwen2.5:7b    # modelo recomendado para máquinas com 8GB RAM
# ollama pull qwen2.5:14b # baixe apenas se possuir 16GB+ de RAM
```

Verifique se estão disponíveis:
```bash
ollama list
```

### 4. Verifique a configuração

Nenhuma chave de API é necessária, pois a busca web utiliza o DuckDuckGo de forma gratuita. Confirme apenas que o Ollama está rodando:
```bash
curl http://localhost:11434
# deve retornar: Ollama is running
```

---

## Uso

```bash
python main.py
```

O CLI vai guiar você por quatro perguntas:

**1. Ferramentas** (o que você quer comparar ou analisar):
```text
podman e docker
kafka e flink
ollama
prometheus e grafana
```

**2. Contexto** (para qual situação específica):
```text
ambiente de desenvolvimento local no Linux
pipeline de ingestão de logs em tempo real
rodando LLMs com até 8GB de RAM
observability em stack FastAPI com docker compose
```

**3. Foco** (qual aspecto aprofundar):
```text
1. comparação geral
2. performance / throughput
3. custo
4. migração
5. integração
6. segurança
7. hardware limitado / edge
8. quantização / modelos locais
```

**4. Perguntas** (o que o artigo deve responder explicitamente):
```text
como configurar modo rootless?
docker-compose funciona sem mudanças no podman?
qual tem menor uso de RAM em idle?
[enter para terminar]
```

**5. Critérios de validação** (checklist manual após a geração):
```text
menciona que podman é daemonless
tem tabela comparativa com pelo menos 4 critérios
[enter para terminar]
```

---

## O que é gerado

```text
artigos/
└── podman-e-docker_20250407_1430.md   # artigo final

output/
├── debug_research.md                  # dados brutos da pesquisa
├── debug_analysis.md                  # análise antes da escrita
├── urls_podman.txt                    # URLs consultadas por ferramenta
├── urls_docker.txt
└── metrics.json                       # métricas de cada execução

.memory/
├── episodic.json                      # log de eventos
└── procedural.json                    # correções que funcionaram
```

---

## Configuração avançada

Edite `spec/article_spec.yaml` para personalizar. Ajuste os modelos de acordo com a sua memória RAM disponível.

```yaml
# trocar modelos
models:
  researcher: "qwen2.5:7b"
  writer:     "qwen2.5:7b"   # altere para 14b apenas se tiver 16GB+ RAM
  critic:     "qwen2.5:7b"

# ajustar temperatura
ollama:
  temperature:
    researcher: 0.1   # mais baixo = mais factual
    writer:     0.3   # mais alto = mais criativo

# mudar regras de qualidade
article:
  quality_rules:
    min_references: 3
    min_errors: 2
```

---

## Limitações Críticas e Conhecidas

**O pipeline tem um gargalo na ingestão de dados.** A pesquisa baseia-se nos resultados resumidos fornecidos pelo DuckDuckGo. O sistema não lê o código HTML completo das páginas de destino. Isso força o modelo a preencher lacunas com seu conhecimento prévio, o que pode gerar alucinações técnicas. Verifique rigorosamente os dados factuais gerados antes da publicação.

**Rate Limits do DuckDuckGo.** Como a ferramenta faz scraping direto no buscador de forma não-oficial, rodar o pipeline múltiplas vezes em um curto período pode resultar em bloqueio temporário (rate limit) do seu IP pelo DuckDuckGo.

**Atenção aos limites de memória RAM.** O carregamento de modelos 14B em máquinas com 8GB de RAM causará esgotamento de memória e paginação severa no disco. Configure o `article_spec.yaml` para usar modelos 7B se o seu hardware for limitado.

---

## Como a memória melhora o sistema ao longo do tempo

Na primeira execução a memória está vazia. O sistema se comporta como qualquer pipeline sem estado.

A partir da segunda execução, se houve correções na primeira, essas lições são injetadas no contexto do writer antes de gerar. Problemas recorrentes são resolvidos antes de acontecer.

Para inspecionar o que foi aprendido:
```bash
cat .memory/procedural.json
cat .memory/episodic.json
```

---

## Exemplos de inputs

Os exemplos abaixo cobrem os casos de uso mais comuns. Use como referência para montar seus próprios inputs.

---

### Comparação geral — container runtime

```
Ferramentas: podman e docker
Contexto:    ambiente de desenvolvimento local no Linux para times de engenharia
Foco:        1 (comparação geral)

Perguntas:
  como configurar modo rootless em cada um?
  docker-compose funciona sem mudanças no podman?
  qual tem menor uso de RAM e CPU em idle?
  podman é daemonless e o que isso muda na prática?

Critérios:
  menciona que podman é daemonless e docker não
  explica rootless com comando real
  tem tabela comparativa com pelo menos 4 critérios
  não recomenda um sem justificativa técnica para o contexto
```

**Quando usar esse padrão:** duas ferramentas que fazem a mesma coisa e você precisa decidir qual adotar. O foco de comparação geral gera queries balanceadas para os dois lados.

---

### Integração — observability stack

```
Ferramentas: prometheus e grafana
Contexto:    observability em stack FastAPI com 3 serviços rodando em docker compose
Foco:        5 (integração)

Perguntas:
  como expor métricas do FastAPI para o prometheus?
  como configurar o grafana para usar o prometheus como datasource?
  qual o scrape interval recomendado para não sobrecarregar a aplicação?
  como criar um dashboard básico de latência e requisições por segundo?

Critérios:
  tem exemplo de scrape config do prometheus
  tem código Python real para expor métricas no FastAPI
  não trata prometheus e grafana como concorrentes
  menciona prometheus-client ou starlette-prometheus
```

**Quando usar esse padrão:** duas ferramentas que trabalham juntas, não concorrentes. Use foco de integração para que o writer não tente compará-las mas sim mostrar como combiná-las.

---

### Hardware limitado — LLM local

```
Ferramentas: ollama
Contexto:    rodando LLMs localmente com até 8GB de RAM no Ubuntu
Foco:        8 (quantização / modelos locais)

Perguntas:
  quais modelos funcionam bem com 8GB de RAM?
  qual a diferença prática entre Q4 e Q8?
  como medir tokens por segundo para comparar modelos?
  tem como rodar dois modelos ao mesmo tempo nessa RAM?

Critérios:
  RAM dos modelos recomendados está abaixo de 8GB
  menciona Q4 ou Q8 com impacto real em qualidade
  tem pelo menos um modelo concreto recomendado
  tem comando real do ollama (ollama run, ollama pull)
```

**Quando usar esse padrão:** ferramenta única com foco em restrição de hardware. O foco de quantização gera queries específicas sobre modelos e memória — sem ele o artigo ficaria genérico demais.

---

### Streaming — pipeline de dados

```
Ferramentas: kafka e flink
Contexto:    pipeline de ingestão de logs de aplicação em tempo real
Foco:        5 (integração)

Perguntas:
  como kafka e flink se encaixam no mesmo pipeline?
  qual a garantia de entrega padrão e como mudar para exactly-once?
  como lidar com backpressure quando o flink não acompanha o kafka?
  qual o mínimo de recursos para rodar os dois juntos em produção?

Critérios:
  explica o papel de cada um no pipeline (broker vs processador)
  menciona at-least-once ou exactly-once
  tem exemplo de job flink consumindo tópico kafka
  não trata kafka e flink como substitutos
```

**Quando usar esse padrão:** ferramentas do mesmo ecossistema com papéis complementares. Sem o foco de integração e as perguntas certas, o modelo tende a comparar ao invés de integrar.

---

### Object storage — ferramentas obscuras

```
Ferramentas: versitygw e garage
Contexto:    object storage self-hosted compatível com S3 em ambiente air-gapped
Foco:        1 (comparação geral)

Perguntas:
  quais operações da API S3 cada um suporta?
  como configurar replicação entre nós?
  funciona sem acesso à internet após instalado?
  qual o consumo de disco e RAM com 1TB de dados?

Critérios:
  menciona compatibilidade com API S3
  tem exemplo com aws-cli ou boto3
  não inventa features que não existem
  referências incluem github.com
```

**Quando usar esse padrão:** ferramentas pouco documentadas fora do GitHub. As perguntas guiam a busca para o que realmente importa e o critério "não inventa features" é o mais importante para detectar alucinação.

---

### Workflow — orquestração de microsserviços

```
Ferramentas: temporal e conductor
Contexto:    orquestração de workflows em microsserviços com falhas parciais e retries
Foco:        1 (comparação geral)

Perguntas:
  o que é durable execution e como cada um implementa?
  como cada um lida com falha parcial no meio de um workflow?
  como funciona o mecanismo de retry e backoff?
  qual a diferença entre orquestração e coreografia?

Critérios:
  explica durable execution com clareza
  tem exemplo de workflow com pelo menos 2 steps
  não confunde orquestração com coreografia
  menciona compensação ou rollback em caso de falha
```

**Quando usar esse padrão:** conceitos abstratos onde a distinção conceitual é tão importante quanto a técnica. As perguntas forçam o modelo a ir além da superfície e as perguntas conceituais ("o que é durable execution?") revelam se houve alucinação de conceito.

---

### Referência rápida — qual foco usar

| Situação | Foco recomendado |
|----------|-----------------|
| Duas ferramentas que fazem a mesma coisa | comparação geral |
| Preciso decidir qual adotar para o time | comparação geral |
| Ferramentas que trabalham juntas | integração |
| Hardware com pouca RAM ou CPU | hardware limitado / edge |
| Rodando modelos de IA localmente | quantização / modelos locais |
| Migrando de uma ferramenta para outra | migração |
| Custo é o critério principal | custo |
| Ambiente de produção com requisitos de segurança | segurança |
| Pipeline de dados com volume alto | performance / throughput |

---

## Roadmap

- [ ] Plugar um extrator de web scraping completo (ex: Playwright/BeautifulSoup) para contornar a limitação de ler apenas os snippets de busca.
- [ ] Testes unitários para componentes determinísticos.
- [ ] Feedback loop: checklist manual alimenta a memória automaticamente.
- [ ] Observability persistente com histórico de execuções.
- [ ] Suporte a múltiplos idiomas na spec.
