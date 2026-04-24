---
name: feynman-technique
description: Turn resolved bugs, implementation lessons, reviews, and debugging sessions into evidence-grounded engineering learning notes with Feynman explanations, recurrence guardrails, and daily or weekly review digests.
---

# /feynman-technique — Engineering Learning Journal

Use this skill when the user invokes `/feynman-technique`, asks to log engineering learnings, wants a daily/weekly learning digest, or wants a resolved issue turned into a transferable lesson.

The goal is not a diary. The goal is a learning pipeline: evidence → root cause → Feynman explanation → prediction check → guardrail → spaced review.

## Commands

```text
/feynman-technique                         Log all resolved fixes/lessons from this session
/feynman-technique <description>           Anchor on one issue, but still capture other fixes found
/feynman-technique review                  Generate today's daily digest
/feynman-technique review YYYY-MM-DD       Generate a digest for a specific date
/feynman-technique retro                   Weekly retrospective + pattern clustering (last 7 days)
/feynman-technique retro <N>               Retrospective over the last N days
/feynman-technique quiz                    Active-recall questions from recent entries
/feynman-technique explain <entry-title>   Re-explain one entry using the Feynman loop
/feynman-technique gaps                    Summarize repeated categories and blind spots
```

## Paths and Storage

The skill must be installable anywhere. Do not hardcode absolute paths. Resolve paths this way:

- **Skill base directory:** the directory containing this `SKILL.md`. Bundled resources and scripts are resolved relative to that directory.
- **Journal directory:** resolve in order:
  1. `FEYNMAN_TECHNIQUE_DIR` if set; use it directly.
  2. `FEYNMAN_TECHNIQUE_BASE_DIR` if set; store under `<base>/feynman-technique`.
  3. Default to `~/Documents/feynman-technique`.

If no writable location can be resolved, stop and ask the user to set `FEYNMAN_TECHNIQUE_DIR`.

### First Run

On the very first invocation (no journal files exist yet in the resolved directory), tell the user where the journal will be stored and offer alternatives:

```
Journal will be saved to: <resolved-path>
Alternatives: ~/Downloads/feynman-technique, or any other path.
Proceed with <resolved-path>? (yes / provide alternative)
```

If the user provides an alternative, set `FEYNMAN_TECHNIQUE_DIR` for the session and proceed. On subsequent runs, skip this prompt — the directory already has files.

Use `scripts/journal.py` for deterministic file I/O (append, dedup, list, digest, quiz, gaps) when available.

## Evidence Rules

Entries must be **generic and transferable** — no references to internal file paths, module names, proprietary table/column names, or codebase-specific identifiers. The journal is a personal learning artifact, not a codebase audit trail.

Evidence is a **blog-style breakdown** of what happened, structured as 3-5 bullet points:
- What was the task or context?
- What went wrong (the observable symptom)?
- What was the root cause?
- How was it resolved?
- What's the takeaway?

Use generic, anonymized examples (e.g., "a query referenced a non-existent column" not "query used `deviceappversion` on `hive.prod_views.session`"). The goal is to teach the *principle*, not document the *instance*.

If full conversation context is unavailable, recover evidence from `git diff`, recent files, tests, logs, or the user's description. Ask for clarification only when the lesson would otherwise be speculative.

## Quality Bar

Every entry must be generic, transferable, and testable:

- **No codebase references** — no file paths, function names, internal table/column names, app IDs, or project-specific identifiers. Use anonymized descriptions instead.
- **Headers are principles** — the title should be the transferable lesson, not the specific bug (e.g., "Always verify schema before writing queries" not "Fixed deviceappversion column bug").
- Explain the mental-model gap, not just the symptom.
- State a general principle that applies outside this bug.
- Add a prediction check whose answer proves the concept was understood.
- Add a guardrail: test, assertion, lint, monitoring, checklist, or design rule.
- Follow `resources/evidence-bank.md` for external references. Do not invent company incidents.

---

## Mode: Log (default)

Triggered by: `/feynman-technique` or `/feynman-technique <description>`

### Step 1: Scan the Full Conversation

Scan the **entire** conversation from top to bottom. Identify **every** distinct bug fix, issue resolution, or problem solved — not just the most recent one.

A "fix" is any of:
- A code change that resolved a broken behavior
- A config/environment correction
- A design decision that unblocked a stuck problem
- A debugging session that revealed a root cause (even if the fix was trivial)

Collect all of them. If the user provided a description, use it to anchor one specific issue, but still capture all others found in the conversation.

**Deduplication:** If the same underlying issue was revisited multiple times (e.g., first attempt failed, second succeeded), treat it as one entry — capture the final resolution, not each attempt.

**Severity gate — only log fixes worth learning from:**

A fix is worth logging if it falls into one of these tiers:

| Tier | What qualifies | Examples |
|---|---|---|
| **Critical** | Production breakage, data corruption, security flaw, system crash | Race condition causing data loss, SQL injection, unhandled null crashing the app |
| **Medium** | Incorrect behavior requiring system understanding to diagnose and fix | Wrong API contract assumption, stale state bug, query returning wrong results, async ordering issue |
| **Architectural** | A design or structural decision that shapes how the system evolves | Choosing service vs. tool placement, refactoring a layer boundary, adopting a new pattern |
| **Best practice** | A deliberate choice to follow an established engineering principle | Adding partition pruning to Trino queries, using parameterized queries instead of f-strings, proper error propagation |

**Drop everything else — these have no transferable principle:**
- Typo fixes, renaming, cosmetic text changes
- Simple find-and-replace or grep-and-fix operations
- Adding/removing imports that the compiler/linter told you about
- Lint fixes, formatting, missing commas, style adjustments
- Copy-paste of boilerplate with no judgment involved
- Config value changes with obvious intent (e.g., changing a port number)

**The test:** *"Does this fix carry a principle that would prevent a class of bugs, not just this one instance?"* If no, skip it.

### Step 2: For Each Fix — Classify

Assign exactly one category per fix using `resources/categories.md`. Add impact and surface metadata.

### Step 3: For Each Fix — Write the Learning Note

Use the template from `resources/templates.md`. Run the Feynman pass from `resources/feynman-method.md`. Add a concrete recurrence guardrail.

The entry format:

```
### <transferable principle as title>
`<category>` · `<impact>` · `<surface>`

> **TL;DR:** <one sentence — the entire lesson distilled for 30-second journal skimming>

**Evidence:**
- <what was the task or context?>
- <what went wrong — the observable symptom?>
- <what was the root cause?>
- <how was it resolved?>
- <what's the takeaway?>

**The gap:** <1 sentence — what you misunderstood or assumed incorrectly>
**The principle:** <1 sentence — the general, transferable rule you now carry forward>
**Guardrail:** <test, assertion, lint rule, monitoring, checklist, or design change to prevent recurrence>

**Feynman explanation:** <plain-English explanation a junior engineer would understand, no project-specific jargon>
**Where I was fuzzy:** <the part initially hand-waved or assumed>
**Prediction check:** <question whose answer proves understanding>
   <details><summary>Answer</summary><the answer></details>

**In the wild:** (1-2 substantive bullets REQUIRED — see `resources/evidence-bank.md`)
- <language spec, framework doc, SRE practice, post-mortem, or authoritative guide that codifies this principle>
- <a second reference from a different angle — e.g., a linting rule, a blog post describing a real incident, or a design pattern book>
<!-- HH:MM -->
```

### Step 4: Save to Daily Journal

1. Resolve journal directory per the Paths and Storage rules above
2. Target file: `YYYY-MM-DD.md` using today's date
3. If the file is new, write the header from `resources/templates.md`
4. If the file already exists, **read it first** — do not duplicate entries that are already logged. Match on the `### title` to detect duplicates.
5. Append each new note preceded by a `---` separator
6. End each note with a timestamp: `<!-- HH:MM -->`
7. Use `scripts/journal.py append --title "<title>"` when available

### Step 5: Confirm

Output all notes to the user. After all notes, add a single **Session Summary** block:

```
Saved <N> entries to <journal-path>/YYYY-MM-DD.md

<note 1>

<note 2>

...

---
**Session summary:** <1 sentence — the dominant theme across today's fixes>
**Review prompts:**
1. <question for note 1 — answer is the principle>
   <details><summary>Answer</summary><the principle from note 1></details>
2. <question for note 2 — answer is the principle>
   <details><summary>Answer</summary><the principle from note 2></details>
...
```

---

## Mode: Review

Triggered by: `/feynman-technique review` or `/feynman-technique review YYYY-MM-DD`

This generates an end-of-day digest and appends it to the bottom of today's (or specified date's) file.

### Step 1: Read the Day's File

1. Determine target date: today if no date given, otherwise the provided `YYYY-MM-DD`
2. Read the day's file from the journal directory
3. If the file doesn't exist or has no entries, tell the user and stop
4. If a `## Daily Digest` section already exists at the bottom, tell the user it's already been generated and stop (don't overwrite)

### Step 2: Analyze All Entries

Parse every `### <title>` entry in the file. For each, extract:
- Category, Principle, Gap, Guardrail, Feynman explanation

Then synthesize across all entries:
- **Category distribution** — which categories appeared and how many times
- **Common thread** — is there a recurring theme or systemic issue?
- **Strongest lesson** — which entry has the most transferable principle?
- **Weakness signal** — what do the gaps collectively reveal about your current blind spots?

### Step 3: Write the Digest

Use the Daily Digest template from `resources/templates.md`. The digest includes:

- What you fixed / What you learned / Your blind spot
- **Explain it like I'm new (Feynman check)** — for each entry, distill the lesson into one plain-English sentence a junior engineer with 6 months of experience would understand
- **Guardrails to add** — highest-leverage guardrails from today's entries
- Scorecard with repeat category tracking
- **In the wild** — 2-3 most impactful entries connected to real-world engineering practices (follow `resources/evidence-bank.md` rules)
- **Review prompts** with collapsible answers

To populate "Repeat categories from prior days": check prior date files. Scan the most recent 5 files and flag any categories that appear in both today and prior days.

### Step 4: Confirm

Output the digest to the user:

```
Daily digest appended to <journal-path>/YYYY-MM-DD.md

<the digest content>
```

---

## Mode: Retro (Weekly Retrospective + Pattern Clustering)

Triggered by: `/feynman-technique retro` or `/feynman-technique retro <N>`

This generates a deep retrospective that clusters your learning patterns, surfaces systemic weaknesses, distills the most critical lessons into a condensed learning digest, and backs every insight with real-world evidence. Default lookback is 7 days; the user can override with any number of days.

### Step 1: Gather All Entries

1. Determine the lookback window: 7 days if no argument given, otherwise `<N>` days
2. Scan the journal directory for all date files within the window
3. If fewer than 2 files exist, tell the user there isn't enough data for a meaningful retro and suggest using `/feynman-technique review` for single-day analysis instead
4. Parse every `### <title>` entry from every file. For each entry, extract:
   - Date (from filename), Title, Category, What broke, Why it broke, The gap, The fix, The principle, Guardrail, Feynman explanation (if present)

### Step 2: Cluster by Pattern

Group entries not just by category, but by **root cause pattern** — entries that share the same underlying systemic issue even if they have different categories. Use this clustering logic:

1. **Category clusters** — group by the 10 categories from `resources/categories.md`
2. **Root cause clusters** — within and across categories, identify entries that share a deeper pattern. Examples:
   - "Assumed API shape without verifying" (could span `contract`, `mental-model`, `data`)
   - "Didn't account for empty/null states" (could span `edge-case`, `state`)
   - "Changed code without testing the full integration path" (could span `mental-model`, `contract`)
3. A single entry can belong to both its category cluster and a root cause cluster

For each cluster with 2+ entries, identify:
- **Pattern name** — a concise label for the recurring mistake (e.g., "Assumption-driven integration")
- **Frequency** — how many times it appeared and on which days
- **Trend** — is it increasing, stable, or decreasing over the window?
- **Representative entries** — the 1-2 entries that best illustrate the pattern

### Step 3: Distill Critical Lessons

From all entries in the window, rank by learning value and select the **top 5 most critical lessons**. Ranking criteria:
1. **Severity** — how much damage would repeating this cause?
2. **Frequency** — how often did this pattern appear?
3. **Transferability** — does the principle apply broadly or only to one narrow case?
4. **Recency** — more recent entries get a slight boost (the lesson is fresher)

For each of the top 5, produce a **condensed learning card**:

```
#### <rank>. <title> (<date>)
`<category>` · `<pattern cluster name>`

**The lesson in one line:** <the principle, rewritten for maximum clarity and memorability>
**Feynman explanation:** <the peer teaching line from the original entry, or generate one if missing>
**Why it matters:** <1 sentence — the real-world consequence of not learning this>
**Your trigger:** <1 sentence — the specific moment in your workflow where you should remember this>
**Guardrail:** <the concrete recurrence prevention from the original entry>

**Evidence from the field:** (follow `resources/evidence-bank.md` rules)
- <company/project — how this lesson plays out at scale>
- <company/project — a notable incident or practice related to this lesson>
- <framework/standard — authoritative source that codifies this principle>
```

### Step 4: Write the Retro

1. Target file: `retro-YYYY-MM-DD.md` in the journal directory (using today's date)
2. If the file already exists, tell the user and ask if they want to overwrite
3. Write the full retrospective:

```
# Weekly Retrospective — YYYY-MM-DD
> Covering <N> days: YYYY-MM-DD to YYYY-MM-DD | <total entries> entries across <total files> sessions

---

## Pattern Clusters

### Cluster: <pattern name> (<N> entries)
**Trend:** <increasing / stable / decreasing>
**Dates:** <list of dates this appeared>
**The pattern:** <2-3 sentences — what systemic behavior or misunderstanding connects these entries>
**Representative entries:**
- <date> — <title>: <1-sentence summary of the gap>
- <date> — <title>: <1-sentence summary of the gap>

**Evidence:** (follow `resources/evidence-bank.md` rules)
- <reference — how this pattern manifests in production systems at scale>
- <reference — a post-mortem, practice, or architectural decision addressing this pattern>
- <reference — authoritative guidance on avoiding this class of issue>

### Cluster: <pattern name> (<N> entries)
...

(repeat for each cluster with 2+ entries)

---

## Top 5 Critical Lessons

<condensed learning cards from Step 3>

---

## Lessons That Stuck

<List entries from the first half of the window whose pattern did NOT recur in the second half. These are principles you've internalized. If none, say "Too early to tell — need more data points.">

## Lessons That Didn't

<List patterns that appeared in BOTH the first and second half of the window. These are your repeat offenders — the habits that need deliberate practice. If none, say "No repeat patterns detected — strong retention this period.">

---

## Trend Analysis

| Metric | Value |
|---|---|
| Total entries | <N> |
| Days active | <N of N possible> |
| Categories hit | <sorted list with counts> |
| Most frequent category | <category> (<N> entries, <X%>) |
| Most frequent pattern | <pattern cluster name> (<N> entries) |
| New categories (not in prior retros) | <list or "none"> |
| Resolved categories (in prior retros, not this one) | <list or "none"> |

## Guardrails To Implement Next

Based on the top 5 lessons and repeat offenders:

1. **<guardrail>** — <which pattern it prevents>
2. **<guardrail>** — <which pattern it prevents>
3. **<guardrail>** — <which pattern it prevents>

## Focus Areas for Next Week

1. **<area>** — <1 sentence: what to do differently and when>
2. **<area>** — <1 sentence: what to do differently and when>
3. **<area>** — <1 sentence: what to do differently and when>

## Active Recall Prompts

> *Read these at the start of each day next week. Answer from memory, then expand to check.*

1. <question — answer is the principle from top lesson 1>
   <details><summary>Answer</summary><the principle from top lesson 1></details>
2. <question — answer is the principle from top lesson 2>
   <details><summary>Answer</summary><the principle from top lesson 2></details>
3. <question — answer is the principle from top lesson 3>
   <details><summary>Answer</summary><the principle from top lesson 3></details>
4. <question — answer is the principle from top lesson 4>
   <details><summary>Answer</summary><the principle from top lesson 4></details>
5. <question — answer is the principle from top lesson 5>
   <details><summary>Answer</summary><the principle from top lesson 5></details>
```

To populate "New categories" and "Resolved categories": check if prior retro files exist (`retro-*.md`). If yes, compare category lists.

### Step 5: Confirm

Output the full retro to the user, then:

```
Retro saved to <journal-path>/retro-YYYY-MM-DD.md

<the full retro content>
```

---

## Mode: Quiz

Triggered by: `/feynman-technique quiz`

Pull review prompts and prediction checks from recent journal entries (last 7 days). Present them as active-recall questions with collapsible answers. Use `scripts/journal.py quiz` when available.

---

## Mode: Explain

Triggered by: `/feynman-technique explain <entry-title>`

Re-explain a specific entry using the full Feynman loop from `resources/feynman-method.md`. Read the entry from the journal, then run all 9 Feynman steps, producing a deeper explanation than the original entry's inline Feynman fields.

---

## Mode: Gaps

Triggered by: `/feynman-technique gaps`

Summarize repeated categories and blind spots across recent entries (last 7 days). Use `scripts/journal.py gaps` when available. Output category frequency counts and all mental-model gaps.

---

## Resources

- Entry and digest templates: `resources/templates.md`
- Feynman learning loop: `resources/feynman-method.md`
- Categories and metadata: `resources/categories.md`
- Safe external reference guidance: `resources/evidence-bank.md`
- Deterministic journal helper: `scripts/journal.py`
