import yaml
from pathlib import Path
from ollama import Client


class AnalystSkill:

    def __init__(self, memory, spec_path="spec/article_spec.yaml"):
        self.memory = memory
        self.spec   = yaml.safe_load(Path(spec_path).read_text())
        self.model  = self.spec["models"]["analyst"]
        self.temp   = self.spec["ollama"]["temperature"]["analyst"]
        timeouts = self.spec["ollama"].get("timeout", {})
        self.timeout = timeouts.get("analyst", timeouts.get("default", 300))
        self.llm    = Client(host=self.spec["ollama"]["base_url"], timeout=self.timeout)

    def run(self, research, tools, context,
            focus="general comparison", questions=None):

        questions = questions or []
        tools_list = [t.strip() for t in tools.lower().replace(" and ", ",").split(",") if t.strip()]
        is_single = len(tools_list) == 1
        is_integration = focus == "integration"

        questions_block = ""
        if questions:
            lista = "\n".join(f"- {q}" for q in questions)
            questions_block = f"\nThe analysis must provide data to answer:\n{lista}\n"

        if is_single:
            table_block = self._single_tool_template(tools_list[0], focus)
        elif is_integration:
            table_block = self._integration_template(tools_list, focus)
        else:
            table_block = self._comparison_template(tools_list, focus)

        prompt = f"""You are a technical analyst. Analyze the research data below.

TOOLS: {tools}
USAGE CONTEXT: {context}
ANALYSIS FOCUS: {focus}
{questions_block}

RESEARCH DATA:
{research}

CRITICAL RULES:
- Produce ONLY what the data supports
- If data doesn't exist in the research, OMIT the line or table cell
- NEVER write "DATA ABSENT", "NOT FOUND", "N/A" or any placeholder
- If an entire table doesn't have enough data, replace it with a paragraph
  explaining what is known
- Empty cells are FORBIDDEN — remove the entire row if there's no data
- NEVER use generic phrases like "consult the documentation" or "as needed"

{table_block}

## PROS
[3 items with technical justification based on data]

## CONS
[3 items with technical justification based on data]

## OPTIMIZATIONS
[3 tips with actual command if available in data]

## RECOMMENDATION
[1 paragraph: recommendation for "{context}" considering "{focus}"]
"""
        resp = self.llm.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temp},
        )

        self.memory.log_event("analysis_done", {
            "tools": tools,
            "focus": focus,
            "mode": "single" if is_single else ("integration" if is_integration else "comparison"),
        })
        return resp.response

    def _comparison_template(self, tools, focus):
        t1, t2 = tools[0], tools[1] if len(tools) > 1 else "alternative"
        return f"""## REQUIREMENTS TABLE
[If there are concrete RAM/CPU data, make the table.
 If there are no official requirements, write a short paragraph explaining why.]

## COMPARISON TABLE
| Criterion | {t1} | {t2} |
|----------|------|------|
[minimum 5 criteria — ONLY those with data for both columns]
[if data exists only for one side, remove the row]"""

    def _integration_template(self, tools, focus):
        return f"""## REQUIREMENTS TABLE
[combined requirements of the complete stack]

## HOW THEY FIT
[explain the role of each tool in the pipeline — who produces, who consumes]

## INTEGRATION TABLE
| Aspect | {tools[0]} | {tools[1] if len(tools) > 1 else ''} | How to connect |
|---------|------|------|---------------|
[minimum 4 aspects with concrete data on how to integrate]"""

    def _single_tool_template(self, tool, focus):
        return f"""## REQUIREMENTS TABLE
[If there are concrete RAM/CPU data, make the table.
 If there are no official requirements, write a short paragraph explaining why.]

## DETAILED ANALYSIS: {tool}
[analysis focused on {focus} with concrete data from research]
[organize by subtopics relevant to the focus]"""
