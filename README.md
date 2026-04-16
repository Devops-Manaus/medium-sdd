# SDD Tech Writer

A comparative technical article generator using local LLMs via Ollama.

You provide the tools, usage context, and questions the article should answer. The system researches (via DuckDuckGo + scraping), analyzes, writes, and validates. Everything runs on your machine without sending data to paid APIs or depending on external keys.

---

## Why SDD

SDD (Spec-Driven Development) is an approach where the **specification is the source of truth**, not the generated code or text. Every output derives from a formal contract defined before execution.

In traditional technical content development, what makes a "good article" lives in the writer's head. Here, it lives in `spec/article_spec.yaml`. This means that:

- The model doesn't decide what is acceptable. The spec does.
- Validation is deterministic, not subjective.
- When the spec changes, behavior changes throughout the entire pipeline.

The practical result is that the system **automatically rejects poor outputs** and attempts to correct them before delivery.

---

## What is being used and why

### Spec (`spec/article_spec.yaml`)
Defines the article contract: mandatory sections, quality rules, scraper configuration, models to use, and Ollama settings. It's the only file you need to edit to change the system's global behavior.

### Skills
Each pipeline stage is a specialized class with a single responsibility. Smaller local models perform better on focused tasks than on giant prompts asking for everything at once.

| Skill | Responsibility |
|-------|-----------------|
| `ResearcherSkill` | Web search (DuckDuckGo) + scraping (Trafilatura/curl_cffi/Playwright) to extract factual data |
| `AnalystSkill` | Transforms raw data into analysis (comparative, integration, or single tool) |
| `WriterSkill` | Composes the article following the spec |
| `CriticSkill` | Validates the article in two layers |

### Critic in two layers
**Layer 1 (Deterministic):** Checks structure, placeholders, invented URLs, empty solutions, and quality minimums. No LLM, no token cost, always reliable.

**Layer 2 (Semantic):** Asks the model if there are internal contradictions, non-existent commands, or impossible numbers. Only runs if layer 1 passed. Semantic problems now also reject the article and generate corrections.

If the article fails, the pipeline automatically attempts to correct it (maximum 3 iterations) before saving.

### Memory
The system learns between executions. When a correction resolves a recurring problem, it is saved and injected as context in subsequent executions. Lessons are prioritized by usage frequency, not just recency.

| Type | What it stores |
|------|-------------|
| Working | Current session state |
| Episodic | Log of what happened (persistent, with rotation) |
| Procedural | Correction recipes that worked |

### Observability
Each stage shows a spinner, execution time, and results in real-time. Metrics from each execution are saved in `output/metrics.json` for later analysis.

---

## Project structure

```text
project/
├── spec/
│   └── article_spec.yaml      # contract - edit here to change behavior
├── memory/
│   └── memory_store.py        # persistent memory between executions
├── validators/
│   └── spec_validator.py      # deterministic validation
├── skills/
│   ├── researcher.py          # search and data extraction
│   ├── analyst.py             # comparative / integration / single tool analysis
│   ├── writer.py              # article generation
│   └── critic.py              # two-layer validation
├── tools/
│   ├── search_tool.py         # DuckDuckGo integration (with retry)
│   └── scraper_tool.py        # content extraction (Trafilatura + curl_cffi + Playwright)
├── logger.py                  # visual output with Rich
├── pipeline.py                # flow orchestration
├── main.py                    # interactive CLI
├── .memory/                   # created automatically
├── output/                    # created automatically
└── articles/                  # generated articles
```

---

## Installation

### 1. Prerequisites

**Rust** (required to compile Python dependencies):
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
rustup default stable
```

**Ollama:**
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# download at https://ollama.com/download/windows
```

**uv** (package manager):
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and configure the project

```bash
git clone <your-repository>
cd sdd-ollama

# create virtual environment with Python 3.12
uv venv --python 3.12
uv add ollama requests python-dotenv pyyaml rich duckduckgo-search trafilatura curl_cffi

# optional — fallback for JavaScript-heavy pages
uv add playwright
playwright install chromium
```

### 3. Download models

Choose models according to your hardware.

**8GB of RAM (no dedicated GPU):**
```bash
ollama pull qwen3:8b
```

**32GB of RAM + 8GB of VRAM (recommended):**
```bash
ollama pull qwen3:8b          # researcher, analyst, critic
ollama pull qwen3:30b-a3b     # writer (MoE — only 3B active per token)
```

Verify they are available:
```bash
ollama list
```

### 4. Verify configuration

No API keys are required. Just confirm that Ollama is running:
```bash
curl http://localhost:11434
# should return: Ollama is running
```

---

## Usage

```bash
python main.py
```

The CLI will guide you through five stages:

**1. Tools** (what you want to compare or analyze):
```text
podman and docker
kafka and flink
ollama
prometheus and grafana
```

**2. Context** (for which specific situation):
```text
local development environment on Linux
real-time log ingestion pipeline
running LLMs with up to 8GB of RAM
observability on FastAPI stack with docker compose
```

**3. Focus** (which aspect to deep dive into):
```text
1. general comparison
2. performance / throughput
3. cost
4. migration
5. integration
6. security
7. limited hardware / edge
8. quantization / local models
```

**4. Questions** (what the article must explicitly answer):
```text
how to configure rootless mode?
does docker-compose work without changes in podman?
which has the lowest RAM usage at idle?
[enter to finish]
```

**5. Validation criteria** (manual checklist after generation):
```text
mentions that podman is daemonless
has comparative table with at least 4 criteria
[enter to finish]
```

---

## What is generated

```text
articles/
└── podman-and-docker_20250407_1430.md   # final article

output/
├── debug_research.md                  # raw research data
├── debug_analysis.md                  # analysis before writing
├── urls_podman.txt                    # URLs consulted by tool
├── urls_docker.txt
└── metrics.json                       # metrics from each execution

.memory/
├── episodic.json                      # event log
└── procedural.json                    # corrections that worked
```

---

## Advanced configuration

Edit `spec/article_spec.yaml` to customize.

```yaml
# models — adjust to your hardware
models:
  researcher: "qwen3:8b"
  analyst:    "qwen3:8b"
  writer:     "qwen3:30b-a3b"   # fallback: qwen3:14b if slow
  critic:     "qwen3:8b"

# temperature
ollama:
  temperature:
    researcher: 0.1   # lower = more factual
    writer:     0.3   # higher = more creative

# context per role
  context_length:
    default: 8192
    writer:  16384

# scraper
research:
  scraper:
    max_chars_per_page: 4000
    max_scrapes_per_tool: 10
    timeout_seconds: 15

# quality rules
article:
  quality_rules:
    min_references: 3
    min_errors: 2
    min_solution_chars: 20
```

---

## Known Critical Limitations

**Scraping may fail on JavaScript-heavy pages.** The system tries 3 cascading strategies: curl_cffi (basic Cloudflare bypass) → Trafilatura (static HTML extraction) → Playwright (full JS rendering). If all fail, it uses the DuckDuckGo snippet as fallback.

**DuckDuckGo rate limits.** Search uses the unofficial DuckDuckGo API with 1.5s delay between queries and automatic retry. Still, running the pipeline many times in sequence may result in temporary IP blocking.

**Watch out for RAM memory limits.** The `qwen3:30b-a3b` model is MoE and runs with offload, but still requires 32GB of RAM. If your hardware is more limited, use `qwen3:8b` for all roles.

**Obscure tools generate shallower articles.** If DuckDuckGo doesn't return good results and the scraper fails on found pages, the article will have gaps. The system now omits data instead of inventing, but content will be shorter.

---

## How memory improves the system over time

On first execution, memory is empty. The system behaves like any stateless pipeline.

From the second execution onwards, if there were corrections in the first, those lessons are injected into the writer's context before generation. Lessons are prioritized by usage frequency — corrections that solved problems across multiple executions appear first.

To inspect what was learned:
```bash
cat .memory/procedural.json
cat .memory/episodic.json
```

### Quick reference — which focus to use

| Situation | Recommended focus |
|----------|-----------------|
| Two tools that do the same thing | general comparison |
| I need to decide which to adopt for the team | general comparison |
| Tools that work together | integration |
| Hardware with little RAM or CPU | limited hardware / edge |
| Running AI models locally | quantization / local models |
| Migrating from one tool to another | migration |
| Cost is the main criterion | cost |
| Production environment with security requirements | security |
| Data pipeline with high volume | performance / throughput |

---

## Roadmap

- [x] ~~Plug in web scraping extractor (Trafilatura) to read full page content~~
- [x] ~~Basic Cloudflare bypass with curl_cffi~~
- [ ] Fallback with Playwright for JavaScript-heavy pages that Trafilatura can't extract
- [ ] Unit tests for deterministic components (validator, memory, search)
- [ ] Feedback loop: manual checklist feeds memory automatically
- [ ] Persistent observability with execution history
- [ ] Multi-language support in spec