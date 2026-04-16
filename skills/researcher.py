import yaml
from pathlib import Path
from ollama import Client

FOCUS_QUERIES: dict[str, list[str]] = {
    "general comparison": [
        "{tool} vs {alternative}",
        "{tool} vs {alternative} when to use which",
        "{tool} vs {alternative} pros cons",
        "{tool} vs {alternative} benchmark comparison 2024 2025",
        "{tool} getting started official docs",
        "{tool} install quickstart tutorial",
        "{tool} common errors site:stackoverflow.com",
        "{tool} troubleshooting FAQ",
        "{tool} minimum requirements hardware",
        "{tool} vs {alternative} features table",
    ],
    "performance / throughput": [
        "{tool} benchmark throughput latency results",
        "{tool} vs {alternative} performance comparison numbers",
        "{tool} tuning performance production best practices",
        "{tool} common bottlenecks site:stackoverflow.com",
        "{tool} load test results concurrent connections",
        "{tool} profiling CPU memory usage under load",
        "{tool} vs {alternative} requests per second benchmark",
        "{tool} performance optimization config flags",
        "{tool} scalability limits production",
        "{tool} resource consumption idle vs peak",
    ],
    "cost": [
        "{tool} pricing model tiers",
        "{tool} pricing calculator",
        "{tool} vs {alternative} cost comparison monthly",
        "{tool} hidden costs egress storage bandwidth",
        "{tool} cost optimization tips reduce bill",
        "{tool} free tier limits what is included",
        "{tool} self hosted vs managed cost comparison",
        "{tool} cost at scale 100k 1M requests",
        "{tool} vs {alternative} total cost of ownership",
        "{tool} pricing changes 2024 2025",
    ],
    "migration": [
        "{tool} migration from {alternative} step by step",
        "{tool} migration guide official docs",
        "{tool} vs {alternative} compatibility layer",
        "{tool} breaking changes migration issues site:stackoverflow.com",
        "{tool} migration tool automated converter",
        "{tool} {alternative} coexistence side by side",
        "{tool} migration gotchas pitfalls real world",
        "{tool} API compatibility {alternative} drop in replacement",
        "{tool} migration rollback strategy",
        "{tool} config differences from {alternative}",
    ],
    "integration": [
        "{tool} {alternative} integration example tutorial",
        "{tool} {alternative} end to end setup guide",
        "{tool} {alternative} getting started together",
        "{tool} connector {alternative} site:github.com",
        "{tool} {alternative} docker compose example",
        "{tool} {alternative} architecture diagram how they fit",
        "{tool} {alternative} example project site:github.com",
        "{tool} exporter plugin {alternative}",
        "{tool} {alternative} common integration errors",
        "{tool} {alternative} production setup best practices",
    ],
    "security": [
        "{tool} security configuration hardening guide",
        "{tool} vs {alternative} security comparison",
        "{tool} authentication authorization setup RBAC",
        "{tool} CVE vulnerabilities site:github.com",
        "{tool} TLS SSL configuration mutual auth",
        "{tool} security best practices production",
        "{tool} rootless unprivileged setup",
        "{tool} secrets management configuration",
        "{tool} audit logging security events",
        "{tool} network policy firewall rules",
    ],
    "limited hardware / edge": [
        "{tool} minimum requirements RAM CPU disk",
        "{tool} raspberry pi ARM installation tutorial",
        "{tool} vs {alternative} resource usage comparison",
        "{tool} low memory configuration optimization",
        "{tool} lightweight alternative embedded edge",
        "{tool} ARM64 aarch64 support",
        "{tool} reduce memory footprint tips",
        "{tool} run on 1GB 2GB 4GB RAM",
        "{tool} disable features save resources",
        "{tool} single node small cluster resource usage",
    ],
    "quantization / local models": [
        "{tool} quantization Q4_K_M Q8_0 quality difference",
        "{tool} recommended models 8GB RAM 16GB RAM list",
        "{tool} tokens per second benchmark results table",
        "{tool} model RAM usage size comparison table",
        "{tool} best models to run locally 2024 2025",
        "{tool} run llama qwen gemma phi mistral RAM required",
        "{tool} how to check memory usage ps verbose",
        "{tool} GGUF model size RAM needed calculator",
        "{tool} compare quantization levels quality loss",
        "{tool} context length RAM impact 2048 4096 8192",
        "{tool} CPU only inference speed tips",
        "{tool} num_thread num_ctx performance tuning",
    ],
}

DEFAULT_QUERIES = [
    "{tool} getting started official docs",
    "{tool} install quickstart tutorial",
    "{tool} vs {alternative}",
    "{tool} vs {alternative} pros cons",
    "{tool} common errors site:stackoverflow.com",
    "{tool} site:github.com",
    "{tool} minimum requirements hardware",
    "{tool} best practices production",
]

# URLs that consume tokens without returning useful data
SKIP_DOMAINS = {
    "youtube.com", "youtu.be", "twitter.com", "x.com",
    "facebook.com", "instagram.com", "tiktok.com",
    "pinterest.com", "reddit.com/gallery",
}

MAX_SCRAPES_PER_TOOL = 10
MAX_CHARS_PER_SCRAPE = 4000


class ResearcherSkill:

    def __init__(self, search_tool, scraper_tool, memory, spec_path="spec/article_spec.yaml"):
        self.search = search_tool
        self.scraper = scraper_tool
        self.memory = memory
        self.spec = yaml.safe_load(Path(spec_path).read_text())
        self.model = self.spec["models"]["researcher"]
        self.temp = self.spec["ollama"]["temperature"]["researcher"]
        timeouts = self.spec["ollama"].get("timeout", {})
        self.timeout = timeouts.get("researcher", timeouts.get("default", 300))
        self.llm = Client(host=self.spec["ollama"]["base_url"], timeout=self.timeout)

    # ------------------------------------------------------------------
    # public
    # ------------------------------------------------------------------
    def run(self, tool, alternative="", focus="general comparison", questions=None):
        questions = questions or []
        queries = self._build_queries(tool, alternative, focus, questions)

        results_by_query = self.search.search_multi(queries)
        self.search.save_urls(results_by_query, f"output/urls_{tool}.txt")

        context = self._build_context(results_by_query)
        lessons = self.memory.get_lessons_for_prompt()

        questions_block = ""
        if questions:
            lista = "\n".join(f"- {q}" for q in questions)
            questions_block = f"\nSeek specific data to answer:\n{lista}\n"

        prompt = f"""You are a technical researcher. Analyze the data below about {tool}.
Focus of this research: {focus}
{questions_block}
{lessons}

SEARCH DATA:
{context}

CRITICAL RULES:
- Extract ONLY what is in the data above
- If a piece of data does NOT appear in the results, OMIT the entire line
- NEVER write "NOT FOUND", "DATA ABSENT", "N/A" or any placeholder
- If an entire section has no data, write: "No data in results for this section."
- NEVER invent numbers, versions or commands
- Copy EXACT commands from snippets
- URLs marked as SCRAPE_FAILED have only the search snippet — shallow data

Produce the report:

## CONSULTED URLS
[list ONLY URLs that start with https://]

## HARDWARE REQUIREMENTS
[If you found concrete values, list them. Otherwise, briefly explain
 why there are no official requirements if the data suggests this,
 or omit this section.]

## INSTALLATION COMMANDS
[exact commands from snippets in ```bash blocks]

## COMMON ERRORS
[errors found in results with cause and solution]

## DATA RELEVANT TO: {focus}
[specific information about the focus]

## MENTIONED ALTERNATIVES
[tools compared in the results]
"""
        resp = self.llm.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temp},
        )

        self.memory.log_event("research_done", {
            "tool": tool,
            "focus": focus,
            "queries": queries,
            "scrape_stats": self._last_scrape_stats,
        })
        return resp.response

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------
    def _build_queries(self, tool, alternative, focus, questions):
        templates = FOCUS_QUERIES.get(focus, DEFAULT_QUERIES)
        alt = alternative or "alternatives"
        queries = [
            q.replace("{tool}", tool).replace("{alternative}", alt)
            for q in templates
        ]
        for q in questions[:4]:
            queries.append(f"{tool} {q}")
        return queries

    # ------------------------------------------------------------------
    # context
    # ------------------------------------------------------------------
    def _build_context(self, results_by_query):
        lines = []
        seen_urls: set[str] = set()
        scrape_ok = 0
        scrape_fail = 0
        total_scrapes = 0

        for query, results in results_by_query.items():
            lines.append(f"\n### Search: {query}")

            for r in results:
                url = r.get("url", "")
                if not url.startswith("http") or url in seen_urls:
                    continue
                if any(d in url for d in SKIP_DOMAINS):
                    continue
                seen_urls.add(url)

                if total_scrapes >= MAX_SCRAPES_PER_TOOL:
                    lines.append(f"URL: {url}")
                    lines.append(f"Summary: {r.get('snippet', '')}")
                    lines.append("---")
                    continue

                total_scrapes += 1
                result = self.scraper.extract_text(url)

                if result["status"] == "ok":
                    scrape_ok += 1
                    text = result["text"][:MAX_CHARS_PER_SCRAPE]
                    tag = " [TRUNCATED]" if result.get("truncated") else ""
                    lines.append(f"URL: {url}{tag}")
                    lines.append(f"Extracted Content:\n{text}")
                    lines.append("---")
                else:
                    scrape_fail += 1
                    self.memory.log_event("scrape_failed", {
                        "url": url, "status": result["status"],
                    })
                    snippet = r.get("snippet", "")
                    if snippet:
                        lines.append(f"URL: {url} [SCRAPE_FAILED: {result['status']}]")
                        lines.append(f"Summary (fallback): {snippet}")
                        lines.append("---")

        self._last_scrape_stats = {
            "ok": scrape_ok,
            "fail": scrape_fail,
            "skipped": len(seen_urls) - total_scrapes,
        }
        return "\n".join(lines)
