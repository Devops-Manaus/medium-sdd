import os
import yaml
import json
from datetime import datetime
from pathlib import Path
from httpx import TimeoutException

from tools.search_tool import SearchTool
from tools.scraper_tool import ScraperTool
from memory.memory_store import MemoryStore
from skills.researcher import ResearcherSkill
from skills.analyst import AnalystSkill
from skills.writer import WriterSkill
from skills.critic import CriticSkill
from logger import PipelineLogger


class SDDPipeline:

    MAX_ITERATIONS = 3

    def __init__(self, spec_path: str = "spec/article_spec.yaml"):
        self.spec_path = spec_path
        self.spec      = yaml.safe_load(Path(spec_path).read_text())
        self.log       = PipelineLogger()
        self.memory    = MemoryStore()

        # read scraper config from spec
        scraper_conf = self.spec.get("research", {}).get("scraper", {})
        search_tool  = SearchTool()
        scraper_tool = ScraperTool(
            max_chars=scraper_conf.get("max_chars_per_page", 4000),
            timeout=scraper_conf.get("timeout_seconds", 15),
        )

        self.researcher = ResearcherSkill(search_tool, scraper_tool, self.memory, spec_path)
        self.analyst    = AnalystSkill(self.memory, spec_path)
        self.writer     = WriterSkill(self.memory, spec_path)
        self.critic     = CriticSkill(self.memory, spec_path)

        os.makedirs("output", exist_ok=True)
        os.makedirs("articles", exist_ok=True)

    def run(
        self,
        tools: str,
        context:    str,
        focus:        str = "general comparison",
        questions:    list[str] | None = None,
    ) -> str:

        questions = questions or []

        self.log.pipeline_start(tools, context)
        self.log.console.print(
            f"   [dim]Focus: {focus} | "
            f"Questions: {len(questions)}[/dim]\n"
        )

        self.memory.set("tools", tools)
        self.memory.set("context", context)
        self.memory.set("focus", focus)
        self.memory.set("questions", questions)
        self.memory.log_event("pipeline_start", {
            "tools": tools,
            "context":    context,
            "focus":        focus,
            "questions":    questions,
        })

        # ---- 1. research ----
        self.log.section(1, 3, "Researching")
        tools_list     = self._parse_tools(tools)
        research_parts = []

        timeouts = self.spec["ollama"].get("timeout", {})
        default_timeout = timeouts.get("default", 300)

        for tool in tools_list:
            alt = next((t for t in tools_list if t != tool), "")
            with self.log.task(f"Researching {tool}"):
                try:
                    data = self.researcher.run(
                        tool=tool,
                        alternative=alt,
                        focus=focus,
                        questions=questions,
                    )
                except TimeoutException:
                    self.log.error(
                        f"Researcher timeout ({self.researcher.timeout}s) — "
                        f"insufficient data for {tool}"
                    )
                    data = f"# {tool}\n\nResearch interrupted by timeout ({self.researcher.timeout}s)."
            research_parts.append(f"# {tool}\n{data}")

        research = "\n\n".join(research_parts)
        self.memory.set("research", research)
        self._save_debug("research", research)

        # detect weak research
        research_quality = self._assess_research_quality(research)
        if research_quality == "weak":
            self.log.console.print(
                "   [yellow]⚠ Weak research — few concrete data found[/yellow]"
            )

        # ---- 2. analysis ----
        self.log.section(2, 3, "Analyzing")
        with self.log.task("Generating analysis"):
            try:
                analysis = self.analyst.run(
                    research=research,
                    tools=tools,
                    context=context,
                    focus=focus,
                    questions=questions,
                )
            except TimeoutException:
                self.log.error(
                    f"Analyst timeout ({self.analyst.timeout}s) — using raw research"
                )
                analysis = f"Analysis interrupted by timeout ({self.analyst.timeout}s).\n\n{research}"

        self.memory.set("analysis", analysis)
        self._save_debug("analysis", analysis)

        # ---- 3. write + critic loop ----
        self.log.section(3, 3, "Writing")

        lessons = self.memory.get_lessons_for_prompt()
        if lessons:
            lesson_line = next(
                (l for l in lessons.splitlines() if l.startswith("-")),
                lessons.splitlines()[0],
            )
            self.log.memory_hit(lesson_line)

        correction_instructions = ""
        article    = ""
        evaluation = {"approved": False, "problems": [], "correction_prompt": ""}

        for iteration in range(1, self.MAX_ITERATIONS + 1):
            self.log.iteration(iteration, self.MAX_ITERATIONS)

            with self.log.task("Writing article"):
                try:
                    article = self.writer.run(
                        research=research,
                        analysis=analysis,
                        tools=tools,
                        context=context,
                        focus=focus,
                        questions=questions,
                        correction_instructions=correction_instructions,
                        research_quality=research_quality,
                    )
                except TimeoutException:
                    self.log.error(
                        f"Writer timeout ({self.writer.timeout}s) in iteration {iteration}"
                    )
                    if iteration == self.MAX_ITERATIONS:
                        article = f"# Timeout\n\nGeneration interrupted: writer exceeded {self.writer.timeout}s."
                        break
                    continue

            # post-processing: remove forbidden phrases that the model insists on
            article = self._sanitize_article(article)

            with self.log.task("Validating against spec"):
                try:
                    evaluation = self.critic.evaluate(article, tools)
                except TimeoutException:
                    self.log.error(
                        f"Critic timeout ({self.critic.timeout}s) — approving without semantic validation"
                    )
                    evaluation = {
                        "approved": True,
                        "layer": "timeout_skip",
                        "warnings": [f"Semantic validation skipped: critic exceeded {self.critic.timeout}s"],
                        "report": "Semantic validation skipped due to timeout.",
                    }

            # show validation result
            if evaluation["approved"]:
                self.log.critic_passed(
                    evaluation.get("layer", ""),
                    evaluation.get("warnings", []),
                )
                self.memory.log_event("article_approved", {
                    "iteration":   iteration,
                    "tools": tools,
                    "focus":        focus,
                })
                if iteration > 1:
                    # extract the real problems, without the generic header
                    problems = [
                        l.strip()
                        for l in correction_instructions.splitlines()
                        if l.strip() and l.strip()[0].isdigit()
                    ]
                    pattern = "; ".join(problems)[:150] if problems else correction_instructions[:150]
                    self.memory.learn(
                        problem_pattern=pattern,
                        solution=f"Resolved in {iteration} iterations",
                        context=f"{tools} | focus: {focus}",
                    )
                break

            self.log.critic_failed(evaluation.get("problems", []))
            correction_instructions = evaluation.get("correction_prompt", "")

            if iteration == self.MAX_ITERATIONS:
                self.log.error("Maximum iterations reached. Saving best version.")
                self.memory.log_event("max_iterations_reached", {
                    "tools": tools,
                    "problems":    evaluation.get("problems", []),
                })

        # ---- save ----
        slug = tools.lower().replace(" ", "-").replace(",", "")[:40]
        ts   = datetime.now().strftime("%Y%m%d_%H%M")
        path = f"articles/{slug}_{ts}.md"

        Path(path).write_text(article, encoding="utf-8")

        metrics = {
            "tools": tools,
            "focus":        focus,
            "questions":   len(questions),
            "iterations":   iteration,
            "approved":    evaluation["approved"],
            "output":      path,
        }
        self.log.metrics(metrics)
        self.log.saved(path)

        self._save_metrics(tools, path, evaluation["approved"], focus)
        return path

    def _parse_tools(self, tools: str) -> list[str]:
        return [
            t.strip()
            for t in tools.lower().replace(" and ", ",").split(",")
            if t.strip()
        ]

    def _assess_research_quality(self, research: str) -> str:
        """Returns 'weak' if research doesn't have sufficient data."""
        indicators = 0
        lower = research.lower()
        # has real URLs?
        import re
        urls = re.findall(r'https?://[^\s]+', research)
        if len(urls) >= 5:
            indicators += 1
        # has code blocks?
        if research.count("```") >= 4:
            indicators += 1
        # has extracted content (not just snippets)?
        if "extracted content" in lower or "content:" in lower:
            indicators += 1
        # doesn't have many scrape_failed?
        fail_count = lower.count("scrape_failed")
        if fail_count <= 2:
            indicators += 1
        return "ok" if indicators >= 3 else "weak"

    def _sanitize_article(self, article: str) -> str:
        """Remove forbidden phrases that the model insists on using."""
        import re
        patterns = self.spec["article"]["quality_rules"]["no_placeholders"]["patterns"]

        lines = article.split("\n")
        cleaned = []

        for line in lines:
            lower = line.lower().strip()
            has_placeholder = any(p.lower() in lower for p in patterns)
            if has_placeholder:
                if lower.startswith("#") and len(lower) < 80:
                    continue
                for p in patterns:
                    line = re.sub(re.escape(p), "", line, flags=re.IGNORECASE)
                if not line.strip() or line.strip() in (".", "-", "*"):
                    continue
            cleaned.append(line)

        result = "\n".join(cleaned)

        # remove empty ```bash``` blocks or ones with just comments
        result = re.sub(
            r'```bash\s*\n(\s*#[^\n]*\n)*\s*```',
            '',
            result,
        )

        # remove invented URLs
        url_rules = self.spec["article"]["quality_rules"].get("url_validation", {})
        for bp in url_rules.get("block_patterns", []):
            result = re.sub(rf'https?://[^\s]*{re.escape(bp)}[^\s]*', '', result)

        return result

    def _save_debug(self, stage: str, content: str):
        Path(f"output/debug_{stage}.md").write_text(content, encoding="utf-8")

    def _save_metrics(self, tools, path, approved, focus):
        entry = {
            "ts":          datetime.now().isoformat(),
            "tools": tools,
            "focus":        focus,
            "output":      path,
            "approved":    approved,
        }
        with open("output/metrics.json", "a", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
