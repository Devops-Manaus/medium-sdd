import yaml
from pathlib import Path
from ollama import Client


class WriterSkill:

    def __init__(self, memory, spec_path="spec/article_spec.yaml"):
        self.memory = memory
        self.spec   = yaml.safe_load(Path(spec_path).read_text())
        self.model  = self.spec["models"]["writer"]
        self.temp   = self.spec["ollama"]["temperature"]["writer"]
        timeouts = self.spec["ollama"].get("timeout", {})
        self.timeout = timeouts.get("writer", timeouts.get("default", 300))
        self.llm    = Client(host=self.spec["ollama"]["base_url"], timeout=self.timeout)
        ctx = self.spec["ollama"].get("context_length", {})
        self.ctx_len = ctx.get("writer", ctx.get("default", 8192))

    def run(self, research, analysis, tools, context,
            focus="general comparison", questions=None,
            correction_instructions="", research_quality="ok"):

        questions = questions or []
        lessons = self.memory.get_lessons_for_prompt()

        correction_block = ""
        if correction_instructions:
            correction_block = f"""
############################################################
# MANDATORY CORRECTIONS — THE ARTICLE WAS REJECTED
# If these corrections are not applied, it will be rejected again.
############################################################

{correction_instructions}

WARNING: The previous article was REJECTED for containing the above problems.
- Reread EACH problem listed
- Find the exact text section in the article that causes the problem
- Rewrite ONLY that section
- DO NOT use the forbidden words/phrases anywhere in the article
############################################################
"""

        questions_block = ""
        if questions:
            lista = "\n".join(f"- {q}" for q in questions)
            questions_block = f"""
The article MUST explicitly answer these questions:
{lista}
Each answer must appear clearly in the text.
"""

        lessons_block = f"\n{lessons}\n" if lessons else ""

        research_warning = ""
        if research_quality == "weak":
            research_warning = """
############################################################
# WARNING: RESEARCH DATA IS INSUFFICIENT
# The research returned few concrete data.
# You MUST:
# - OMIT entire sections if there is no data to fill them
# - NEVER invent commands, URLs, model names or numbers
# - Prefer writing "No concrete data found" over inventing
# - Keep the article SHORT if data is scarce
# A short, correct article is better than a long, invented one.
############################################################
"""

        prompt = f"""You are an experienced tech writer. Write a complete technical article.

TOOLS: {tools}
CONTEXT: {context}
FOCUS: {focus}
{questions_block}
{correction_block}
{lessons_block}
{research_warning}

RESEARCH DATA:
{research}

TECHNICAL ANALYSIS:
{analysis}

INVIOLABLE RULES:
1. NEVER use placeholders: [Describe...], [TODO], [X], DATA ABSENT,
   NOT FOUND, N/A — the presence of ANY of these rejects the article
2. NEVER use generic phrases as solutions: "as needed",
   "consult the documentation", "check the configuration" — this rejects
3. If you don't have concrete data, there are 3 options:
   a) Omit the line/section silently
   b) Explain why the data doesn't exist (ex: "doesn't publish official requirements")
   c) Give an estimate based on evidence ("based on community tests, ~500MB")
4. Use ONLY commands that appear in the data above — never invent
5. URLs in references must be ONLY from the consulted URLs in research
6. Every table must have ALL cells filled — if there's no data, remove the row
7. Every solution in Pitfalls must have a real command with at least 20 characters

TEMPLATE (include ALL sections):

# [Descriptive title about {tools}]

> **TL;DR:** [One objective sentence, maximum 20 words]

## What is it and why use it
[2 paragraphs with focus on: {focus}]

## Requirements
[If there is data: table. If there are no official requirements: explain in 1-2 sentences why.]

## Installation
### Method 1: [name]
```bash
[real commands]
```
### Method 2: [name]
```bash
[real commands]
```

## Configuration
[configuration file with real path and content]

## Practical Example
### Scenario: [realistic description for {context}]
[numbered steps with real commands + expected result]

## Common Pitfalls
### ⚠ [Real error name]
**Symptom:** [concrete description]
**Cause:** [technical explanation]
**Solution:**
```bash
[real command with at least 20 characters]
```

### ⚠ [Real error name]
**Symptom:** ...  **Cause:** ...  **Solution:** ...

## Optimization Tips
[minimum 3 tips with real commands when available]

## Conclusion
[trade-offs for {context} considering {focus}]

## References
[minimum 3 real URLs from research, format: - URL]
"""
        resp = self.llm.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": self.temp,
                "num_ctx": self.ctx_len,
            },
        )
        self.memory.log_event("article_written", {"tools": tools})
        return resp.response
