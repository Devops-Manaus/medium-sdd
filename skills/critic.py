import yaml
from pathlib import Path
from ollama import Client
from validators.spec_validator import SpecValidator


class CriticSkill:

    def __init__(self, memory, spec_path="spec/article_spec.yaml"):
        self.memory    = memory
        self.spec      = yaml.safe_load(Path(spec_path).read_text())
        self.model     = self.spec["models"]["critic"]
        self.temp      = self.spec["ollama"]["temperature"]["critic"]
        self.llm       = Client(host=self.spec["ollama"]["base_url"])
        self.validator = SpecValidator(spec_path)

    def evaluate(self, artigo: str, ferramentas: str) -> dict:
        result = self.validator.validate(artigo)

        self.memory.log_event("critic_ran", {
            "ferramentas": ferramentas,
            "passed":      result.passed,
            "problems":    result.problems
        })

        if not result.passed:
            return {
                "approved":          False,
                "layer":             "deterministic",
                "problems":          result.problems,
                "correction_prompt": self.validator.problems_as_prompt(result),
                "report":            result.report()
            }

        semantic_issues = self._semantic_check(artigo, ferramentas)

        return {
            "approved": True,
            "layer":    "semantic",
            "warnings": result.warnings + semantic_issues,
            "report":   result.report()
        }

    def _semantic_check(self, artigo: str, ferramentas: str) -> list[str]:
        prompt = f"""Revise este artigo sobre {ferramentas}.

Liste APENAS problemas factuais óbvios:
- Comando que claramente não existe
- Número claramente impossível
- Contradição interna entre seções

Responda APENAS com lista numerada.
Se não encontrar problemas, responda exatamente: SEM PROBLEMAS

ARTIGO:
{artigo[:3000]}
"""
        resp = self.llm.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temp}
        )
        text = resp.response.strip()
        if "SEM PROBLEMAS" in text.upper():
            return []
        return [
            l.strip()
            for l in text.split("\n")
            if l.strip() and l[0].isdigit()
        ]