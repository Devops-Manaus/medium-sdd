import yaml
from pathlib import Path
from ollama import Client


class WriterSkill:
    def __init__(self, memory, spec_path="spec/article_spec.yaml"):
        self.memory = memory
        self.spec   = yaml.safe_load(Path(spec_path).read_text())
        self.model  = self.spec["models"]["writer"]
        self.temp   = self.spec["ollama"]["temperature"]["writer"]
        self.llm    = Client(host=self.spec["ollama"]["base_url"])

    def run(self, research, analysis, ferramentas, contexto,
            foco="comparação geral", questoes=None,
            correction_instructions=""):
        questoes = questoes or []

        correction_block = ""
        if correction_instructions:
            correction_block = f"""
⚠️ CORREÇÕES OBRIGATÓRIAS DA ITERAÇÃO ANTERIOR:
{correction_instructions}
Corrija esses problemas específicos. Não altere o que já está correto.
"""

        questoes_block = ""
        if questoes:
            lista = "\n".join(f"- {q}" for q in questoes)
            questoes_block = f"""
O artigo DEVE responder explicitamente estas perguntas:
{lista}
Cada resposta deve aparecer claramente no texto.
"""
        prompt = f"""Você é um tech writer experiente. Escreva um artigo técnico completo.

FERRAMENTAS: {ferramentas}
CONTEXTO: {contexto}
FOCO: {foco}
{questoes_block}
{correction_block}

DADOS DE PESQUISA:
{research}

ANÁLISE TÉCNICA:
{analysis}

REGRAS INVIOLÁVEIS:
1. NUNCA use placeholders: [Descreva...], [TODO], [X], DADO AUSENTE,
   NÃO ENCONTRADO, N/A — a presença de QUALQUER UM desses reprova o artigo
2. Se não tem um dado concreto, há 3 opções:
   a) Omita a linha/seção silenciosamente
   b) Explique por que o dado não existe (ex: "não publica requisitos oficiais")
   c) Dê uma estimativa baseada em evidência ("baseado em testes da comunidade, ~500MB")
3. Use APENAS comandos que aparecem nos dados acima
4. URLs em referências devem ser das URLs consultadas
5. Toda tabela deve ter TODAS as células preenchidas — se não tem dado, remova a linha

TEMPLATE (inclua TODAS as seções):

# [Título descritivo sobre {ferramentas}]

> **TL;DR:** [Uma frase objetiva, máximo 20 palavras]

## O que é e por que usar
[2 parágrafos com foco em: {foco}]

## Requisitos
[Se há dados: tabela. Se não há requisitos oficiais: explique em 1-2 frases por quê.]

## Instalação
### Método 1: [nome]
```bash
[comandos reais]
```
### Método 2: [nome]
```bash
[comandos reais]
```

## Configuração
[arquivo de configuração com caminho real e conteúdo]

## Exemplo Prático
### Cenário: [descrição realista para {contexto}]
[passos numerados com comandos reais + resultado esperado]

## Armadilhas Comuns
### ⚠ [Nome do erro real]
**Sintoma:** [descrição concreta]
**Causa:** [explicação técnica]
**Solução:**
```bash
[comando real]
```

### ⚠ [Nome do erro real]
**Sintoma:** ...  **Causa:** ...  **Solução:** ...

## Dicas de Otimização
[mínimo 3 dicas com comandos reais quando disponíveis]

## Conclusão
[trade-offs para {contexto} considerando {foco}]

## Referências
[mínimo 3 URLs reais da pesquisa, formato: - URL]
"""
        resp = self.llm.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temp}
        )
        self.memory.log_event("article_written", {"ferramentas": ferramentas})
        return resp.response