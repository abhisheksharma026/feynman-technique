# Feynman Technique Templates

## Learning Entry Template

```md
### <concise title>
`<category>` · `<impact>` · `<surface>`

> **TL;DR:** <one sentence for fast skimming>

**Evidence:**
- <what was the task or context?>
- <what went wrong?>
- <what was the root cause?>
- <how was it resolved?>
- <what is the takeaway?>

**The gap:** <the incorrect assumption or missing mental model>
**The principle:** <general rule that transfers beyond this bug>
**Guardrail:** <test, assertion, lint rule, monitoring, checklist, or design change>

**Feynman explanation:** <plain-English explanation of the mechanism, no unexplained jargon>
**Toy example:** <minimal version of the same bug or misunderstanding>
**Where I was fuzzy:** <the part initially hand-waved or assumed>
**Prediction check:** <question whose answer proves understanding>
<details><summary>Answer</summary><the answer></details>
**Nearby application:** <one other workflow where this principle may apply>

**In the wild:**
- <authoritative guide, standard, or framework doc that codifies the principle>
- <second reference from a different angle, or "External reference: none needed; local evidence is sufficient.">

**Review prompt:** <active-recall question; answer is the principle or guardrail>
<details><summary>Answer</summary><the answer></details>
<!-- HH:MM -->
```

## Daily Digest Template

```md
---

## Daily Digest

**Entries today:** <N>
**Categories:** <category1> (N), <category2> (N)
**Surfaces:** <frontend/backend/data/etc.>

### What you fixed
<2-3 sentences summarizing the work and shipped fixes.>

### What you learned
<2-3 sentences connecting the repeated mental-model gaps.>

### Your blind spot
<1-2 sentences naming what to verify earlier next time.>

### Explain it like I'm new (Feynman check)
1. <plain-English lesson from entry 1>
2. <plain-English lesson from entry 2>

### Guardrails to add
1. <highest-leverage guardrail>
2. <next guardrail if relevant>

### In the wild
- <reference tied to one of today's strongest lessons>
- <reference tied to another strong lesson>

### Scorecard
| Metric | Value |
|---|---|
| Fixes logged | <N> |
| Categories hit | <list> |
| Most frequent category | <category> |
| Repeat categories from prior days | <list or none> |

### Review prompts consolidated
1. <question>
   <details><summary>Answer</summary><answer></details>
2. <question>
   <details><summary>Answer</summary><answer></details>

> Read these tomorrow morning. Answer from memory before checking.
```

## Weekly Digest Template

```md
# Weekly Retrospective - YYYY-MM-DD

> Covering <N> days: YYYY-MM-DD to YYYY-MM-DD | <total entries> entries across <total files> sessions

**Entries:** <N>
**Top categories:** <category counts>
**Most repeated blind spot:** <summary>

## Pattern Clusters
### Cluster: <pattern name> (<N> entries)
**Trend:** <increasing / stable / decreasing>
**Dates:** <list of dates this appeared>
**The pattern:** <2-3 sentences describing the repeated failure mode>
**Representative entries:**
- <date> - <title>: <summary>
- <date> - <title>: <summary>

## Highest-Leverage Principles
1. <principle>
2. <principle>
3. <principle>

## Guardrails To Implement Next
1. <guardrail>
2. <guardrail>
3. <guardrail>

## Quiz
1. <active recall question>
   <details><summary>Answer</summary><answer></details>
2. <active recall question>
   <details><summary>Answer</summary><answer></details>
3. <active recall question>
   <details><summary>Answer</summary><answer></details>
```
