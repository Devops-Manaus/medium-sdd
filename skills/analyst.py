import yaml
from pathlib import Path
from ollama import Client


class AnalystSkill:
    def __init__(self, memory, spec_path="spec/article_spec.yaml"):
        self.memory = memory
        self.spec   = yaml.safe_load(Path(spec_path).read_text())
        self.model  = self.spec["models"]["analyst"]
        self.temp   = self.spec["ollama"]["temperature"]["analyst"]
        self.llm    = Client(host=self.spec["ollama"]["base_url"])

    def run(self, research, ferramentas, contexto,
            foco="comparação geral", questoes=None):
        questoes_block = ""
        if questoes:
            lista = "\n".join(f"- {q}" for q in questoes)
            questoes_block = (
                f"\nA análise deve fornecer dados para responder:\n{lista}\n"
            )
        prompt = f"""Você é um analista técnico. Analise os dados de pesquisa abaixo.

FERRAMENTAS: {ferramentas}
CONTEXTO DE USO: {contexto}
FOCO DA ANÁLISE: {foco}
{questoes_block}

DADOS DA PESQUISA:
{research}

REGRAS CRÍTICAS:
- Produza APENAS o que os dados suportam
- Se um dado não existe na pesquisa, OMITA a linha ou célula da tabela
- NUNCA escreva "DADO AUSENTE", "NÃO ENCONTRADO", "N/A" ou qualquer placeholder
- Se uma tabela inteira não tem dados suficientes, substitua por um parágrafo
  explicando o que se sabe
- Células vazias são PROIBIDAS — remova a linha inteira se não tiver dado

## TABELA DE REQUISITOS
[Se há dados concretos de RAM/CPU, faça a tabela.
 Se não há requisitos oficiais, escreva um parágrafo curto
 explicando por que (ex: "roda como processo userspace,
 sem requisitos próprios além do OS").]

## TABELA COMPARATIVA
| Critério | [ferramenta 1] | [ferramenta 2] |
|----------|----------------|----------------|
[mínimo 5 critérios — APENAS os que têm dados para ambas as colunas]

## PRÓS
[3 itens com justificativa técnica baseada nos dados]

## CONTRAS
[3 itens com justificativa técnica baseada nos dados]

## OTIMIZAÇÕES
[3 dicas com comando se disponível nos dados]

## RECOMENDAÇÃO
[1 parágrafo: qual ferramenta para "{contexto}" considerando "{foco}"]
"""
        resp = self.llm.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temp}
        )
        self.memory.log_event("analysis_done", {
            "ferramentas": ferramentas, "foco": foco
        })
        return resp.response