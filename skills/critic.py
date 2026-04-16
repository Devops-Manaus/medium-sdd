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
        timeouts = self.spec["ollama"].get("timeout", {})
        self.timeout = timeouts.get("critic", timeouts.get("default", 300))
        self.llm       = Client(host=self.spec["ollama"]["base_url"], timeout=self.timeout)
        self.validator = SpecValidator(spec_path)

    def evaluate(self, article: str, tools: str) -> dict:
        result = self.validator.validate(article)

        self.memory.log_event("critic_ran", {
            "tools": tools,
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

        semantic_issues = self._semantic_check(article, tools)

        if semantic_issues:
            prompt_lines = [
                "The article passed structural validation but has semantic problems:",
                *[f"- {s}" for s in semantic_issues],
                "\nFix ONLY those problems. Keep the rest intact.",
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

    def _semantic_check(self, article: str, tools: str) -> list[str]:
        prompt = f"""Review this article about {tools}.
List ONLY obvious factual problems:
- Command that clearly doesn't exist in that tool
- Clearly impossible number (ex: "consumes 3MB RAM" for a database)
- Internal contradiction between sections
- Import or code path that doesn't exist

Answer ONLY with numbered list of problems found.
If you find no problems, answer exactly: NO PROBLEMS

ARTICLE:
{article[:4000]}
"""
        resp = self.llm.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temp},
        )
        text = resp.response.strip()
        if "NO PROBLEMS" in text.upper():
            return []
        return [
            l.strip()
            for l in text.split("\n")
            if l.strip() and l[0].isdigit()
        ]
