import yaml
from pathlib import Path
from validators.spec_validator import SpecValidator

from llm import LLMClient


class CriticSkill:

    def __init__(self, memory, spec_path="spec/article_spec.yaml"):
        self.memory    = memory
        self.spec      = yaml.safe_load(Path(spec_path).read_text())
        self.llm       = LLMClient(spec_path)
        self.model     = self.llm.model_for_role("critic")
        llm_conf = self.spec.get("llm", {})
        temperatures = llm_conf.get("temperature", self.spec.get("ollama", {}).get("temperature", {}))
        timeouts = llm_conf.get("timeout", self.spec.get("ollama", {}).get("timeout", {}))
        self.temp      = temperatures["critic"]
        self.timeout = timeouts.get("critic", timeouts.get("default", 300))
        self.validator = SpecValidator(spec_path)

    def evaluate(self, artigo: str, ferramentas: str) -> dict:
        result = self.validator.validate(artigo)

        self.memory.log_event("critic_ran", {
            "ferramentas": ferramentas,
            "passed":      result.passed,
            "problems":    result.problems,
            "warnings":    result.warnings,
        })

        if not result.passed:
            return {
                "approved":          False,
                "layer":             "deterministic",
                "problems":          result.problems,
                "correction_prompt": self.validator.problems_as_prompt(result),
                "report":            result.report(),
            }

        semantic_issues = self._semantic_check(artigo, ferramentas)

        if semantic_issues:
            prompt_lines = [
                "O artigo passou na validação estrutural mas tem problemas semânticos:",
                *[f"- {s}" for s in semantic_issues],
                "\nCorrija APENAS esses problemas. Mantenha o resto intacto.",
            ]
            return {
                "approved":          False,
                "layer":             "semantic",
                "problems":          semantic_issues,
                "correction_prompt": "\n".join(prompt_lines),
                "report":            result.report(),
            }

        return {
            "approved": True,
            "layer":    "semantic",
            "warnings": result.warnings,
            "report":   result.report(),
        }

    def _semantic_check(self, artigo: str, ferramentas: str) -> list[str]:
        prompt = f"""Revise este artigo sobre {ferramentas}.
Liste APENAS problemas factuais óbvios:
- Comando que claramente não existe nessa ferramenta
- Número claramente impossível (ex: "consome 3MB de RAM" para banco de dados)
- Contradição interna entre seções
- Import ou path de código que não existe

Responda APENAS com lista numerada de problemas encontrados.
Se não encontrar problemas, responda exatamente: SEM PROBLEMAS

ARTIGO:
{artigo[:4000]}
"""
        resp = self.llm.generate(
            role="critic",
            model=self.model,
            prompt=prompt,
            temperature=self.temp,
            timeout=self.timeout,
        )
        text = resp.response.strip()
        if "SEM PROBLEMAS" in text.upper():
            return []
        return [
            l.strip()
            for l in text.split("\n")
            if l.strip() and l[0].isdigit()
        ]
