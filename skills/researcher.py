import yaml
from pathlib import Path
from ollama import Client


FOCUS_QUERIES: dict[str, list[str]] = {
    "comparação geral": [
        "{tool} vs {alternative}",
        "{tool} getting started official docs",
        "{tool} common errors site:stackoverflow.com",
        "{tool} vs {alternative} when to use",
    ],
    "performance / throughput": [
        "{tool} benchmark throughput latency",
        "{tool} vs {alternative} performance comparison",
        "{tool} tuning performance production",
        "{tool} common bottlenecks site:stackoverflow.com",
    ],
    "custo": [
        "{tool} pricing model",
        "{tool} vs {alternative} cost comparison",
        "{tool} hidden costs egress storage",
        "{tool} cost optimization tips",
    ],
    "migração": [
        "{tool} migration from {alternative}",
        "{tool} vs {alternative} compatibility",
        "{tool} migration guide official",
        "{tool} breaking changes migration issues site:stackoverflow.com",
    ],
    "integração": [
        "{tool} {alternative} integration example",
        "{tool} {alternative} tutorial end to end",
        "{tool} {alternative} getting started together",
        "{tool} connector {alternative} site:github.com",
    ],
    "segurança": [
        "{tool} security configuration",
        "{tool} vs {alternative} security comparison",
        "{tool} authentication authorization setup",
        "{tool} CVE vulnerabilities site:github.com",
    ],
    "hardware limitado / edge": [
        "{tool} minimum requirements RAM CPU",
        "{tool} raspberry pi ARM installation",
        "{tool} vs {alternative} resource usage",
        "{tool} low memory configuration",
    ],
    "quantização / modelos locais": [
        "{tool} quantization Q4 Q8 comparison",
        "{tool} recommended models 8GB RAM",
        "{tool} tokens per second benchmark",
        "{tool} vs {alternative} memory usage models",
    ],
}

DEFAULT_QUERIES = [
    "{tool} getting started official docs",
    "{tool} vs {alternative}",
    "{tool} common errors site:stackoverflow.com",
    "{tool} site:github.com",
]


class ResearcherSkill:

    def __init__(self, search_tool, memory, spec_path="spec/article_spec.yaml"):
        self.search = search_tool
        self.memory = memory
        self.spec   = yaml.safe_load(Path(spec_path).read_text())
        self.model  = self.spec["models"]["researcher"]
        self.temp   = self.spec["ollama"]["temperature"]["researcher"]
        self.llm    = Client(host=self.spec["ollama"]["base_url"])

    def run(self, tool, alternative="", foco="comparação geral", questoes=None):
        questoes = questoes or []
        queries  = self._build_queries(tool, alternative, foco, questoes)

        results_by_query = self.search.search_multi(queries)
        self.search.save_urls(results_by_query, f"output/urls_{tool}.txt")

        context = self._build_context(results_by_query)
        lessons = self.memory.get_lessons_for_prompt()

        questoes_block = ""
        if questoes:
            lista = "\n".join(f"- {q}" for q in questoes)
            questoes_block = f"\nBusque dados específicos para responder:\n{lista}\n"
        prompt = f"""Você é um pesquisador técnico. Analise os dados abaixo sobre {tool}.
Foco desta pesquisa: {foco}
{questoes_block}
{lessons}

DADOS DA BUSCA:
{context}

REGRAS CRÍTICAS:
- Extraia APENAS o que está nos dados acima
- Se um dado NÃO aparece nos resultados, OMITA a linha inteira
- NUNCA escreva "NÃO ENCONTRADO", "DADO AUSENTE", "N/A" ou qualquer placeholder
- Se uma seção inteira não tem dados, escreva: "Sem dados nos resultados para esta seção."
- NUNCA invente números, versões ou comandos
- Copie comandos EXATOS dos snippets

Produza o relatório:

## URLS CONSULTADAS
[liste APENAS URLs que começam com https://]

## REQUISITOS DE HARDWARE
[Se encontrou valores concretos, liste-os. Senão, explique brevemente
 por que não existem requisitos oficiais se os dados sugerirem isso,
 ou omita esta seção.]

## COMANDOS DE INSTALAÇÃO
[comandos exatos dos snippets em blocos ```bash]

## ERROS COMUNS
[erros encontrados nos resultados com causa e solução]

## DADOS RELEVANTES PARA: {foco}
[informações específicas sobre o foco]

## ALTERNATIVAS MENCIONADAS
[ferramentas comparadas nos resultados]
"""
        resp = self.llm.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temp}
        )
        self.memory.log_event("research_done", {
            "tool": tool, "foco": foco, "queries": queries
        })
        return resp.response

    def _build_queries(self, tool, alternative, foco, questoes):
        templates = FOCUS_QUERIES.get(foco, DEFAULT_QUERIES)
        alt = alternative or "alternatives"
        queries = [
            q.replace("{tool}", tool).replace("{alternative}", alt)
            for q in templates
        ]
        for q in questoes[:2]:
            queries.append(f"{tool} {q}")
        return queries

    def _build_context(self, results_by_query):
        lines = []
        for query, results in results_by_query.items():
            lines.append(f"\n### Busca: {query}")
            for r in results[:4]:
                url = r.get("url", "")
                if url.startswith("http"):
                    lines.append(f"URL: {url}")
                lines.append(f"Resumo: {r['snippet']}")
                lines.append("---")
        return "\n".join(lines)