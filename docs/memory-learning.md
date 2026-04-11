# Memory and Learning System

This document explains the procedural memory system used in the SDD-OLLAMA pipeline to enable learning from validation feedback and iterative article improvement.

## Overview

The pipeline implements a **procedural memory** approach where validation feedback is captured and used to guide the LLM's next iteration, enabling a "learning" loop over multiple refinement cycles.

### What is Procedural Memory in This Context?

Procedural memory (in cognitive science terms) refers to memory of how to do things—behavioral patterns and skills rather than facts or events. In this project, procedural memory means:

- **Recording what went wrong**: When an article fails validation, we capture the specific problem
- **Capturing the correction**: We document the spec rule that was violated and how to fix it
- **Feeding back to the LLM**: In the next iteration, the LLM receives the feedback and adjusts its behavior
- **Reinforcing good patterns**: Over multiple iterations, the LLM learns to avoid the same mistakes

This is **per-run learning**, not persistent learning. The memory is ephemeral—it lasts only for the duration of one article generation pipeline.

---

## How It Works: The Feedback Loop

### Step 1: Article Generation

The Writer skill generates an initial article based on research and analysis:

```
┌─────────────────────────────────────────────────┐
│ Writer Skill                                    │
│ Generates article from research & analysis     │
└────────────────────┬────────────────────────────┘
                     │
                     v
              Article (v1)
```

### Step 2: Validation

The Critic skill runs deterministic validation against the spec:

```
┌─────────────────────────────────────────────────┐
│ Critic Skill + SpecValidator                    │
│ Runs 11+ validation rules from spec            │
└────────────────────┬────────────────────────────┘
                     │
                     v
        ValidationResult {
          passed: bool
          problems: [str]
          spec_references: [str]  ← NEW: Rule violations
          corrections: dict       ← NEW: How to fix
        }
```

### Step 3: Feedback Generation

Enhanced error messages are constructed with actionable guidance:

```
Validation Result: FAILED

FEEDBACK:
- Problem: "Seção ausente: requisitos"
  📋 Spec Rule: article.required_sections
  ✓ Correção: Adicione a seção '# Requisitos' ao artigo

- Problem: "Placeholder não preenchido: '[TODO'"
  📋 Spec Rule: article.quality_rules.no_placeholders
  ✓ Correção: Substitua '[TODO' por conteúdo real ou remova a linha

GUIDANCE:
O artigo tem os seguintes problemas que DEVEM ser corrigidos:
1. Seção ausente: requisitos
2. Placeholder não preenchido: '[TODO'

Reescreva o artigo corrigindo APENAS esses problemas.
Mantenha todo o conteúdo existente que está correto.
```

### Step 4: Memory Logging

The validation results and feedback are logged to the memory store:

```python
# In CriticSkill.evaluate()
self.memory.log_event("critic_ran", {
    "ferramentas": ferramentas,
    "passed": result.passed,
    "problems": result.problems,
    "warnings": result.warnings,
    "spec_references": result.spec_references,  # NEW
})
```

This creates an episodic memory record of what went wrong.

### Step 5: LLM Learns from Feedback

The enhanced feedback is included in the LLM's next prompt:

```python
# In CriticSkill.evaluate()
correction_prompt_enhanced = (
    "FEEDBACK COM REFERÊNCIA À SPEC:\n\n" +
    detailed_feedback +                    # ← Includes spec rules
    "\n\n" +
    correction_prompt_base                 # ← Includes problems list
)

# The LLM receives this in the next iteration
# Pipeline passes correction_prompt to Writer for next iteration
```

### Step 6: Article Refined

The Writer skill receives the feedback and incorporates it:

```
Article (v1) + Feedback
    ↓
LLM: "I see, I need to:
      - Add the 'Requisitos' section
      - Replace [TODO with actual content
      - Keep everything else the same"
    ↓
Article (v2) ← Refined based on feedback
```

### Step 7: Iteration Loop

Steps 2-6 repeat until:
- Article passes validation, OR
- Max iterations (3) is reached

```
Iteration 1: Article v1 → Validate → Problems → Feedback → Article v2
Iteration 2: Article v2 → Validate → Problems → Feedback → Article v3
Iteration 3: Article v3 → Validate → PASSED ✅ OR Max reached
```

---

## Example: Learning the "No Placeholders" Rule

### Iteration 1: First Attempt

**LLM writes:**
```markdown
# Armadilhas

## Common Error: Memory Leak
[TODO: Describe symptoms and solutions]

Solução:
```bash
# Check memory usage
[TODO: Add specific command]
```
```

**Validation fails:**
```
Problems:
1. Placeholder não preenchido: '[TODO'
   📋 Spec: article.quality_rules.no_placeholders
   ✓ Fix: Replace '[TODO' with actual content or remove the line

2. Solução vazia/genérica em armadilha
   📋 Spec: article.quality_rules.solution_content
   ✓ Fix: Provide actual code/commands (min 20 chars)
```

**Memory record:**
```json
{
  "event": "critic_ran",
  "iteration": 1,
  "problems": [
    "Placeholder não preenchido: '[TODO'",
    "Solução vazia/genérica em armadilha"
  ],
  "spec_references": [
    "article.quality_rules.no_placeholders",
    "article.quality_rules.solution_content"
  ]
}
```

### Iteration 2: Learning

**LLM receives feedback:**
```
FEEDBACK COM REFERÊNCIA À SPEC:

- Placeholder não preenchido: '[TODO'
  📋 Spec Rule: article.quality_rules.no_placeholders
  ✓ Correção: Replace '[TODO' with actual content

- Solução vazia/genérica em armadilha
  📋 Spec Rule: article.quality_rules.solution_content
  ✓ Correção: Provide code with >20 characters

The article has these problems that MUST be fixed:
1. Placeholder not filled: '[TODO'
2. Empty solution in armadilhas section

Rewrite the article fixing ONLY these problems.
Keep all existing content that is correct.
REMINDER: If no data available, OMIT the line. Never write placeholders.
```

**LLM writes (improved):**
```markdown
# Armadilhas

## Common Error: Memory Leak
The application consumes increasing memory over time, eventually running out of heap space.

Sintoma: OutOfMemoryError after several hours of operation

Solução:
```bash
# Check memory usage per process
ps aux | grep java | grep -v grep

# Monitor heap dumps
jmap -dump:live,format=b,file=heap.bin <pid>
```
```

**Validation result:**
```
✓ Article passes armadilhas validation!

No more placeholder errors.
Solution block now has 156 characters (minimum 20).
```

### What the LLM Learned

Through this feedback loop, the LLM has learned:
1. **No placeholders rule**: Don't use `[TODO]`, replace with actual content
2. **Solution specificity**: Provide real commands, not generic advice
3. **Actionable instructions**: Include actual shell commands that users can run

---

## Memory Store Architecture

The memory system is implemented in three layers:

### 1. Working Memory (RAM, Session-Only)

Stores current session state and in-flight data:

```python
class MemoryStore:
    def __init__(self, path: str = ".memory"):
        self._working: dict = {}  # ← Current session state
```

Used for:
- Storing intermediate research data
- Holding the current article being processed
- Tracking iteration count

**Lifetime**: Cleared when pipeline completes or crashes

### 2. Episodic Memory (Persistent Log)

Records what happened during execution:

```json
{
  "episodic.json": [
    {
      "event": "research_completed",
      "timestamp": "2026-04-11T14:30:00",
      "tool": "k3s",
      "urls_found": 42
    },
    {
      "event": "critic_ran",
      "iteration": 1,
      "passed": false,
      "problems": ["Seção ausente: requisitos"],
      "spec_references": ["article.required_sections"]
    },
    {
      "event": "critic_ran",
      "iteration": 2,
      "passed": true,
      "problems": []
    }
  ]
}
```

Used for:
- Post-mortem analysis of what went wrong
- Learning which tools/searches are most effective
- Understanding failure patterns

**Lifetime**: Rotated and archived (keeps last 500 events)

### 3. Procedural Memory (Learned Patterns)

Stores successful solutions and patterns:

```json
{
  "procedural.json": {
    "avoid_patterns": [
      "[TODO",
      "[Descreva",
      "conforme necessário"
    ],
    "required_sections": [
      "tldr",
      "o_que_e",
      "requisitos",
      "..."
    ],
    "successful_structures": [
      {
        "section": "armadilhas",
        "pattern": "Erro: X\nSintoma: Y\nSolução:\n```\ncode\n```",
        "success_rate": 0.95
      }
    ]
  }
}
```

Used for:
- Guiding future article generation (not currently implemented)
- Improving prompts based on past successes
- Avoiding known pitfalls

**Lifetime**: Persistent across multiple runs (potential future enhancement)

---

## Spec References and Corrections

The enhanced ValidationResult now includes spec-aware feedback:

### ValidationResult Structure

```python
@dataclass
class ValidationResult:
    passed: bool
    problems: list[str]
    warnings: list[str]
    spec_references: list[str]    # NEW: e.g., "article.required_sections"
    corrections: dict             # NEW: problem → hint mapping
```

### Example Enhanced Result

```python
result = validator.validate(article)

# result.problems:
[
    "Seção ausente: requisitos",
    "Placeholder não preenchido: '[TODO'"
]

# result.spec_references:
[
    "article.required_sections",
    "article.quality_rules.no_placeholders"
]

# result.corrections:
{
    "Seção ausente: requisitos": "Adicione a seção '# Requisitos' ao artigo",
    "Placeholder não preenchido: '[TODO'": "Substitua '[TODO' por conteúdo real ou remova a linha"
}
```

---

## Limitations and Caveats

### 1. Per-Run Learning Only

Learning is **ephemeral**—it only lasts for the duration of one article generation:

```
Pipeline starts:
  Iteration 1: LLM learns rule X
  Iteration 2: LLM applies learning from iteration 1
  Iteration 3: LLM applies learning from iterations 1-2
Pipeline ends:
  Learning is discarded
  Next article generation starts fresh
```

**Why**: This is simpler to implement and safer than persistent learning across runs.

### 2. Limited Feedback Cycles

Max iterations = 3:

```
Iteration 1: ❌ 5 problems
Iteration 2: ❌ 2 problems
Iteration 3: ✅ 0 problems OR ⏱️ Max reached
```

The LLM has only 2 feedback cycles to learn and improve.

**Why**: Time/cost constraints from LLM API calls and timeout limits (900 seconds total).

### 3. Prompt Injection Risk

Learning relies on injecting feedback into the LLM prompt:

```python
# The feedback is text, not structured data
# The LLM must understand and follow instructions
correction_prompt = "O artigo tem os seguintes problemas: \n" + problems
```

If feedback is unclear or contradictory, the LLM might not learn correctly.

**Mitigation**: Feedback is generated from deterministic validation rules, ensuring clarity.

### 4. No Persistent Learning Across Sessions

This is a design choice (not a limitation):

```
Session 1: Generates article about k3s ✅
  Memory: Learned k3s best practices (discarded)

Session 2: Generates article about k3s again ❌
  Memory: Starts fresh, doesn't benefit from session 1
```

**Future enhancement**: Could persist procedural memory in `procedural.json` and load it at pipeline start.

### 5. Semantic Feedback is LLM-Dependent

Semantic validation uses LLM for factual accuracy:

```python
def _semantic_check(self, article: str, ferramentas: str) -> list[str]:
    prompt = f"Review this article about {ferramentas}..."
    resp = self.llm.generate(...)  # ← Another LLM call
```

This semantic feedback is less deterministic and harder to "learn from" in a structured way.

---

## Procedural Memory in Action: Complete Example

### The Article: k3s Installation Guide

### Iteration 1

**LLM generates:**
```markdown
# TLDR
[TODO: Write summary]

# O que é
k3s [Descreva o que é k3s]

# Requisitos
[Insira requisitos de hardware]
```

**Validation:**
```
❌ FAILED - 3 blocking problems:
1. Placeholder não preenchido: '[TODO'
2. Placeholder não preenchido: '[Descreva'
3. Placeholder não preenchido: '[Insira'
```

**Memory logs:**
```json
{
  "event": "critic_ran",
  "iteration": 1,
  "passed": false,
  "problems": 3,
  "spec_rules_violated": [
    "article.quality_rules.no_placeholders",
    "article.quality_rules.no_placeholders",
    "article.quality_rules.no_placeholders"
  ]
}
```

### Iteration 2

**LLM receives feedback:**
```
The article has these problems that MUST be fixed:
1. Placeholder not filled: '[TODO'
   Spec Rule: article.quality_rules.no_placeholders
   Fix: Replace '[TODO' with actual content

2. Placeholder not filled: '[Descreva'
   Spec Rule: article.quality_rules.no_placeholders
   Fix: Replace '[Descreva' with actual content

3. Placeholder not filled: '[Insira'
   Spec Rule: article.quality_rules.no_placeholders
   Fix: Replace '[Insira' with actual content

REMINDER: If no data, OMIT the line. Never write placeholders.
```

**LLM generates (improved):**
```markdown
# TLDR
k3s is a lightweight Kubernetes distribution for edge computing and IoT.

# O que é
k3s is a certified Kubernetes distribution designed for resource-constrained environments. It removes unnecessary components while maintaining full API compatibility.

# Requisitos
- CPU: 2+ cores (ARM64 supported)
- RAM: 512 MB minimum per node
- Kernel: 3.10+ with cgroup support
- Container runtime: containerd or docker
```

**Validation:**
```
✓ PASSED - No placeholders detected!
⚠ Warning: Only 1 URL found, minimum 3 required
```

**Memory logs:**
```json
{
  "event": "critic_ran",
  "iteration": 2,
  "passed": false,
  "problems": 0,
  "warnings": 1,
  "spec_rules_violated": ["article.quality_rules.min_references"]
}
```

### Iteration 3

**LLM receives feedback:**
```
The article passed structural validation!

However, there is 1 non-blocking warning:
- Referências insuficientes: 1 URLs, mínimo 3

Add references to authoritative sources.
```

**LLM generates (final):**
Adds 3+ HTTPS references at the end.

**Validation:**
```
✅ PASSED - All validation rules satisfied!
- No placeholders
- 3 HTTPS references
- All 10 required sections
- Valid solution content
```

**Result**: Article approved for publication.

---

## Future Enhancements

### 1. Persistent Procedural Memory

Save learned patterns across sessions:

```python
# At pipeline end, save successful patterns
procedural_memory = {
    "successful_structures": [
        {
            "tool": "k3s",
            "section": "requisitos",
            "pattern": "- CPU: 2+ cores\n- RAM: 512MB\n...",
            "success_rate": 0.95
        }
    ]
}
```

### 2. Learning Score Tracking

Track which rules the LLM learned in this session:

```python
learning_score = {
    "article.quality_rules.no_placeholders": {
        "problems_iteration1": 5,
        "problems_iteration2": 1,
        "problems_iteration3": 0,
        "learned": True
    }
}
```

### 3. Cross-Session Pattern Recognition

Analyze episodic memory to identify common failures:

```python
# Find most common validation failures across all runs
failure_patterns = {
    "placeholder_too_common": {
        "count": 247,
        "percentage": 0.68,
        "typical_location": "armadilhas section"
    }
}
```

### 4. Semantic Memory Integration

Store semantic facts learned (beyond this session):

```python
semantic_memory = {
    "k3s": {
        "minimum_ram_gb": 1,
        "supports_arm64": True,
        "primary_use_case": "edge computing"
    }
}
```

---

## Debugging Memory Issues

### Check Memory State

```bash
# View current memory contents
cat .memory/episodic.json | tail -20

# Check procedural memory
cat .memory/procedural.json

# View working memory (during execution)
# Memory is in-RAM only, not directly inspectable
```

### Common Issues

**Problem**: LLM doesn't seem to learn from feedback
- **Cause**: Feedback not in prompt template
- **Fix**: Check `correction_prompt` is passed to LLM in pipeline.py

**Problem**: Memory files keep growing
- **Cause**: `MAX_EPISODIC = 500` not enforced
- **Fix**: Manual cleanup: `rm .memory/episodic.json`

**Problem**: Same errors repeated across iterations
- **Cause**: Feedback prompt not clear enough
- **Fix**: Review feedback message format in critic.py

---

## Key Takeaways

1. **Procedural memory** = Learning from validation feedback over iterations
2. **Per-run learning** = Feedback persists only during one pipeline execution
3. **Three-layer memory** = Working (RAM), Episodic (logs), Procedural (patterns)
4. **Enhanced ValidationResult** = Now includes spec_references and corrections
5. **Feedback loop** = Article → Validate → Feedback → Refine → Iterate
6. **Limitations** = 3 iterations max, per-run only, relies on LLM understanding
7. **Future** = Potential persistent learning across sessions

The memory system enables iterative improvement of articles through validation feedback, dramatically improving quality compared to single-pass generation.
