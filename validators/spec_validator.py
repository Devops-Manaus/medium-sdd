import re
import yaml
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValidationResult:
    passed:   bool
    problems: list[str]
    warnings: list[str]

    def report(self) -> str:
        lines = []
        if self.problems:
            lines.append("PROBLEMS (blocking):")
            for p in self.problems:
                lines.append(f"  ✗ {p}")
        if self.warnings:
            lines.append("WARNINGS (non-blocking):")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        if self.passed:
            lines.append("✓ Article passed all validations")
        return "\n".join(lines)


class SpecValidator:

    def __init__(self, spec_path="spec/article_spec.yaml"):
        self.spec = yaml.safe_load(Path(spec_path).read_text())
        self._rules = self.spec["article"]["quality_rules"]

    def validate(self, article, sections=None):
        problems = []
        warnings = []
        text_lower = article.lower()

        active_sections = sections or self.spec["article"]["required_sections"]

        section_patterns = {
            "tldr":             ["tl;dr", "tldr", "quick summary"],
            "what_is":          ["what is", "why use", "introduction"],
            "requirements":     ["requirement", "hardware", "resource"],
            "installation":     ["install"],
            "configuration":    ["configur"],
            "practical_example":  ["example", "use case", "practical"],
            "pitfalls":       ["pitfall", "common error", "common problem",
                                 "pitfall", "⚠"],
            "optimizations":      ["optim", "tip", "performance"],
            "conclusion":        ["conclusion", "conclus", "trade-off", "verdict"],
            "references":      ["reference", "referenc", "sources"],
            "architecture":      ["architecture", "architecture", "component"],
            "throughput":       ["throughput", "messages/second", "msgs/s"],
            "delivery_guarantees":["at-least-once", "exactly-once", "guarantee"],
            "s3_compatibility":["s3 compat", "api s3", "s3 api"],
            "replication":       ["replication", "replica"],
            "recommended_models": ["recommended model", "recommended model"],
            "quantization":      ["quantization", "quantization", "q4", "q8"],
            "benchmark":        ["benchmark", "tokens/s", "tokens per second"],
            "migration":         ["migration", "migration", "migrate"],
            "security":        ["security", "security", "authentication"],
        }

        for section in active_sections:
            patterns = section_patterns.get(section, [section.replace("_", " ")])
            if not any(p in text_lower for p in patterns):
                problems.append(f"Missing section: {section}")

        for pattern in self._rules["no_placeholders"]["patterns"]:
            if pattern.lower() in text_lower:
                problems.append(f"Unfilled placeholder: '{pattern}'")

        urls_real = re.findall(r'https?://[^\s\)\"\'\]]+', article)
        min_refs = self._rules["min_references"]
        if len(urls_real) < min_refs:
            problems.append(
                f"Insufficient references: {len(urls_real)} URLs, minimum {min_refs}"
            )

        url_rules = self._rules.get("url_validation", {})
        block = url_rules.get("block_patterns", [])
        for url in urls_real:
            for bp in block:
                if bp in url:
                    problems.append(f"Invalid/placeholder URL: {url}")
                    break

        error_markers = re.findall(
            r'(error:|error:|pitfall|problem:|⚠|symptom:)', text_lower
        )
        min_errors = self._rules.get("min_errors", 2)
        if len(error_markers) < min_errors:
            warnings.append(
                f"Few documented errors: {len(error_markers)}, "
                f"recommended {min_errors}"
            )

        min_sol = self._rules.get("min_solution_chars", 20)
        pitfall_blocks = re.findall(
            r'(?:solution|solu[^\s]*)[:\s]*```[a-z]*\n(.*?)```',
            article, re.IGNORECASE | re.DOTALL
        )
        for block in pitfall_blocks:
            content = block.strip()
            if len(content) < min_sol:
                problems.append(
                    f"Empty/generic solution in pitfall: "
                    f"'{content[:40]}' ({len(content)} chars, minimum {min_sol})"
                )

        hw = self._rules.get("hardware_sanity")
        if hw:
            max_ram = hw.get("max_ram_minimum_gb", 2)
            ram_values = re.findall(r'(\d+)\s*gb', text_lower)
            for val in ram_values:
                if int(val) > max_ram * 2:
                    warnings.append(
                        f"Suspicious RAM: {val}GB — verify if correct"
                    )

        code_blocks = re.findall(r'```', article)
        if len(code_blocks) < 4:
            warnings.append(
                "Few code blocks — verify if commands were included"
            )

        table_rows = re.findall(r'\|(.+)\|', article)
        for row in table_rows:
            cells = [c.strip() for c in row.split('|')]
            if any(c == '' for c in cells if not re.match(r'^-+$', c)):
                warnings.append("Table with empty cell detected")
                break

        return ValidationResult(
            passed=len(problems) == 0,
            problems=problems,
            warnings=warnings,
        )

    def problems_as_prompt(self, result):
        if result.passed:
            return ""
        lines = ["The article has the following problems that MUST be fixed:"]
        for i, p in enumerate(result.problems, 1):
            lines.append(f"{i}. {p}")
        lines.append(
            "\nRewrite the article fixing ONLY those problems."
        )
        lines.append("Keep all existing content that is correct.")
        lines.append(
            "REMINDER: If there's no data, OMIT the line. "
            "Never write placeholders."
        )
        return "\n".join(lines)
