#!/usr/bin/env python3
"""Feynman Technique journal helper.

Deterministic support for appending entries, deduping by title, listing entries,
and generating daily/weekly review material.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
RESOURCES_DIR = SKILL_DIR / "resources"
ROOT_MARKER = ".feynman-technique-root"

DATE_FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
RETRO_FILE_RE = re.compile(r"^retro-\d{4}-\d{2}-\d{2}\.md$")
ENTRY_RE = re.compile(r"^###\s+(.+)$", re.MULTILINE)
META_RE = re.compile(r"^`([^`]+)`\s*$", re.MULTILINE)
FIELD_HEADER_RE = re.compile(r"^(> )?\*\*([^*]+):\*\*\s*(.*)$", re.MULTILINE)
DETAILS_RE = re.compile(r"(?s)<details><summary>Answer</summary>\s*(.*?)\s*</details>")

IMPACT_WEIGHTS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

CATEGORY_REFERENCES = {
    "mental-model": [
        "Runtime or framework documentation is the right source of truth for lifecycle and execution behavior."
    ],
    "contract": [
        "API and schema documentation should be treated as the contract boundary before implementation."
    ],
    "state": [
        "Framework state-management guidance is the right reference when data can drift from the current source of truth."
    ],
    "timing": [
        "Concurrency and retry guidance is the right reference when ordering or async behavior can change outcomes."
    ],
    "data": [
        "Database or query-engine documentation is the right reference for schema, null, and aggregation behavior."
    ],
    "config": [
        "Deployment and environment configuration should be validated against documented runtime assumptions."
    ],
    "edge-case": [
        "Boundary conditions should be covered with explicit examples for empty, null, and low-volume inputs."
    ],
    "design": [
        "Architecture guidance should move fixes to the ownership boundary instead of patching symptoms."
    ],
    "testing": [
        "Contract and integration testing guidance is the right reference when local correctness does not prove system correctness."
    ],
    "operations": [
        "SRE guidance is the right reference for guardrails around observability, retries, and operational safety."
    ],
}

PATTERN_RULES = [
    (
        "Boundary states were not modeled",
        ("null", "empty", "none", "missing", "boundary", "edge", "zero"),
    ),
    (
        "Assumption-driven integration",
        ("contract", "schema", "shape", "envelope", "api", "response"),
    ),
    (
        "Timing and ordering were treated as stable",
        ("race", "timing", "async", "retry", "ordering", "lifecycle", "debounce"),
    ),
    (
        "State drifted from the source of truth",
        ("state", "stale", "cache", "invalidate", "sync", "derived state"),
    ),
    (
        "Data assumptions were not verified",
        ("query", "column", "aggregation", "denominator", "dataset", "data", "sql"),
    ),
    (
        "Configuration assumptions were not verified",
        ("config", "environment", "flag", "dependency", "routing", "build", "deploy"),
    ),
    (
        "The local fix was not validated end to end",
        ("integration", "end-to-end", "full path", "workflow", "mock", "over-mocked", "test"),
    ),
    (
        "Ownership and abstraction boundaries were off",
        ("design", "boundary", "ownership", "layer", "service", "component", "abstraction"),
    ),
    (
        "Operational safety was too implicit",
        ("monitor", "logging", "incident", "observability", "alert", "operations"),
    ),
]


def _path_from_env(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else None


def default_journal_root() -> Path:
    configured = _path_from_env("FEYNMAN_TECHNIQUE_DIR")
    if configured:
        return configured

    base = _path_from_env("FEYNMAN_TECHNIQUE_BASE_DIR")
    if base:
        return base / "feynman-technique"

    return Path.home() / "Documents" / "feynman-technique"


def _marker_path(path: Path) -> Path:
    return path / ROOT_MARKER


def _is_initialized(path: Path) -> bool:
    if _marker_path(path).exists():
        return True
    if not path.exists():
        return False
    for child in path.iterdir():
        if DATE_FILE_RE.match(child.name) or RETRO_FILE_RE.match(child.name):
            return True
    return False


def _touch_marker(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _marker_path(path).write_text(
        "Confirmed Feynman Technique journal root.\n",
        encoding="utf-8",
    )


def _confirm_first_run(path: Path) -> Path:
    if os.environ.get("FEYNMAN_TECHNIQUE_AUTO_INIT") == "1":
        _touch_marker(path)
        return path

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise SystemExit(
            "First run confirmation required.\n"
            f"Journal will be saved to: {path}\n"
            "Alternatives: ~/Downloads/feynman-technique, or any other path.\n"
            "Re-run interactively to confirm, or set FEYNMAN_TECHNIQUE_AUTO_INIT=1 for automation."
        )

    print(f"Journal will be saved to: {path}")
    print(
        "Alternatives: ~/Downloads/feynman-technique, or any other path."
    )
    response = input(f"Proceed with {path}? (yes / provide alternative)\n> ").strip()
    if response.lower() in {"y", "yes"}:
        _touch_marker(path)
        return path
    if response:
        alt = Path(response).expanduser()
        _touch_marker(alt)
        return alt
    raise SystemExit("Journal initialization cancelled.")


def journal_dir(require_write: bool = False) -> Path:
    path = default_journal_root()
    if require_write and not _is_initialized(path):
        path = _confirm_first_run(path)
    if require_write:
        try:
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
        except OSError as exc:
            raise SystemExit(
                f"Feynman Technique cannot write to {path}. Set FEYNMAN_TECHNIQUE_DIR to a writable directory."
            ) from exc
    return path


def day_path(day: str, require_write: bool = False) -> Path:
    return journal_dir(require_write=require_write) / f"{day}.md"


def retro_path(day: str, require_write: bool = False) -> Path:
    return journal_dir(require_write=require_write) / f"retro-{day}.md"


def header(day: str) -> str:
    return (
        f"# Engineering Learnings - {day}\n\n"
        "> Each entry captures evidence, root cause, the mental-model gap, "
        "a Feynman explanation, a transferable principle, and a recurrence guardrail.\n"
    )


def ensure_file(day: str) -> Path:
    path = day_path(day, require_write=True)
    if not path.exists():
        path.write_text(header(day), encoding="utf-8")
    return path


def _entries_only(text: str) -> str:
    return text.split("\n## Daily Digest", 1)[0].rstrip()


def _collapse(text: str) -> str:
    return " ".join(part.strip() for part in text.splitlines() if part.strip()).strip()


def _strip_details(text: str) -> str:
    return DETAILS_RE.sub("", text or "").strip()


def _first_sentence(text: str) -> str:
    flat = _collapse(_strip_details(text))
    if not flat:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", flat, maxsplit=1)
    return parts[0]


def _bullets(text: str) -> list[str]:
    items = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            items.append(stripped[2:].strip())
    return items


def _field_sections(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    matches = list(FIELD_HEADER_RE.finditer(body))
    for idx, match in enumerate(matches):
        name = match.group(2).strip()
        inline = match.group(3).rstrip()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        tail = body[match.end():end].strip("\n")
        content = inline.strip()
        if tail:
            content = "\n".join(part for part in (content, tail) if part).strip()
        content = re.sub(r"(?m)^\s*<!--.*?-->\s*$", "", content)
        content = re.sub(r"(?m)^\s*---\s*$", "", content)
        fields[name] = content.strip()
    return fields


def _question_and_answer(text: str, fallback: str = "") -> tuple[str, str]:
    raw = (text or "").strip()
    if not raw:
        return "", fallback.strip()
    match = DETAILS_RE.search(raw)
    if not match:
        return _collapse(raw), fallback.strip()
    answer = _collapse(match.group(1))
    question = _collapse(DETAILS_RE.sub("", raw))
    return question, answer or fallback.strip()


def _parse_meta(block: str) -> tuple[str, str, str, str]:
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("### "):
            continue
        code_spans = re.findall(r"`([^`]+)`", stripped)
        if len(code_spans) >= 3:
            parts = [part.strip() for part in code_spans]
            category = parts[0] if len(parts) > 0 else "unknown"
            impact = parts[1] if len(parts) > 1 else ""
            surface = parts[2] if len(parts) > 2 else ""
            extra = " · ".join(parts[3:]) if len(parts) > 3 else ""
            return category, impact, surface, extra
        match = META_RE.match(stripped)
        if not match:
            continue
        parts = [part.strip(" `") for part in match.group(1).split("·")]
        category = parts[0] if len(parts) > 0 else "unknown"
        impact = parts[1] if len(parts) > 1 else ""
        surface = parts[2] if len(parts) > 2 else ""
        extra = " · ".join(parts[3:]) if len(parts) > 3 else ""
        return category, impact, surface, extra
    return "unknown", "", "", ""


def parse_entries(text: str) -> list[dict[str, str]]:
    source = _entries_only(text)
    matches = list(ENTRY_RE.finditer(source))
    entries: list[dict[str, str]] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(source)
        block = source[start:end].strip()
        title = match.group(1).strip()
        category, impact, surface, extra_meta = _parse_meta(block)
        body = block.split("\n", 1)[1] if "\n" in block else ""
        fields = _field_sections(body)
        prediction, prediction_answer = _question_and_answer(
            fields.get("Prediction check", ""),
            fields.get("The principle", ""),
        )
        review_prompt, review_answer = _question_and_answer(
            fields.get("Review prompt", ""),
            fields.get("The principle", ""),
        )
        entries.append(
            {
                "title": title,
                "category": category or "unknown",
                "impact": impact,
                "surface": surface,
                "extra_meta": extra_meta,
                "tl_dr": fields.get("TL;DR", ""),
                "evidence": fields.get("Evidence", ""),
                "what_broke": fields.get("What broke", ""),
                "why_broke": fields.get("Why it broke", ""),
                "fix": fields.get("The fix", ""),
                "gap": fields.get("The gap", ""),
                "principle": fields.get("The principle", ""),
                "guardrail": fields.get("Guardrail", ""),
                "feynman": fields.get("Feynman explanation", ""),
                "toy_example": fields.get("Toy example", ""),
                "fuzzy": fields.get("Where I was fuzzy", ""),
                "prediction": prediction,
                "prediction_answer": prediction_answer,
                "nearby": fields.get("Nearby application", ""),
                "review_prompt": review_prompt,
                "review_answer": review_answer,
                "wild": fields.get("In the wild", ""),
                "raw_block": block,
            }
        )
    return entries


def titles(text: str) -> set[str]:
    return {entry["title"].strip().lower() for entry in parse_entries(text)}


def append_entry(day: str, title: str, note: str) -> int:
    path = ensure_file(day)
    text = path.read_text(encoding="utf-8")
    if title.strip().lower() in titles(text):
        print(f"duplicate: {title}")
        return 0

    timestamp = datetime.now().strftime("%H:%M")
    clean = note.rstrip()
    if not clean.startswith("### "):
        clean = f"### {title}\n" + clean
    if "<!--" not in clean[-40:]:
        clean = f"{clean}\n<!-- {timestamp} -->"
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n---\n\n")
        fh.write(clean)
        fh.write("\n")
    print(path)
    return 0


def _parse_day(name: str) -> date | None:
    try:
        return date.fromisoformat(name)
    except ValueError:
        return None


def all_day_paths() -> list[Path]:
    jdir = journal_dir(require_write=False)
    if not jdir.exists():
        return []
    dated: list[tuple[date, Path]] = []
    for path in jdir.glob("*.md"):
        if not DATE_FILE_RE.match(path.name):
            continue
        day = _parse_day(path.stem)
        if day is not None:
            dated.append((day, path))
    return [path for _, path in sorted(dated, reverse=True)]


def recent_paths(limit_days: int = 7) -> list[Path]:
    today = date.today()
    earliest = today - timedelta(days=max(limit_days - 1, 0))
    paths: list[tuple[date, Path]] = []
    for path in all_day_paths():
        day = _parse_day(path.stem)
        if day is None:
            continue
        if earliest <= day <= today:
            paths.append((day, path))
    return [path for _, path in sorted(paths, reverse=True)]


def recent_entries(limit_days: int = 7) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in recent_paths(limit_days):
        for entry in parse_entries(path.read_text(encoding="utf-8")):
            entry["date"] = path.stem
            entries.append(entry)
    return entries


def list_entries(day: str) -> int:
    path = day_path(day)
    if not path.exists():
        print(f"missing: {path}")
        return 1
    for entry in parse_entries(path.read_text(encoding="utf-8")):
        print(f"- {entry['title']} [{entry['category']}]")
    return 0


def prior_categories(current_day: str) -> set[str]:
    cats: set[str] = set()
    seen = 0
    for path in all_day_paths():
        if path.stem == current_day:
            continue
        for entry in parse_entries(path.read_text(encoding="utf-8")):
            cats.add(entry["category"])
        seen += 1
        if seen >= 5:
            break
    return cats


def _pattern_label(entry: dict[str, str]) -> str:
    blob = " ".join(
        (
            entry["title"],
            entry["gap"],
            entry["principle"],
            entry["what_broke"],
            entry["why_broke"],
            entry["fix"],
            entry["feynman"],
        )
    ).lower()
    for label, keywords in PATTERN_RULES:
        if any(keyword in blob for keyword in keywords):
            return label
    if entry["category"] and entry["category"] != "unknown":
        return f"{entry['category'].replace('-', ' ').title()} pattern"
    return "General learning pattern"


def _entry_score(entry: dict[str, str], pattern_sizes: dict[str, int]) -> float:
    severity = IMPACT_WEIGHTS.get(entry["impact"], 1)
    frequency = pattern_sizes.get(entry["pattern"], 1)
    transferability = 1 if entry["principle"] else 0
    recency = 0.0
    if entry.get("date"):
        day = _parse_day(entry["date"])
        if day is not None:
            recency = max(0, 14 - (date.today() - day).days) / 14
    return severity * 10 + frequency * 3 + transferability * 2 + recency


def _reference_bullets(entry: dict[str, str]) -> list[str]:
    explicit = _bullets(entry["wild"])
    if explicit:
        return explicit[:3]
    return CATEGORY_REFERENCES.get(
        entry["category"],
        ["External reference: none needed; local evidence is sufficient."],
    )


def _feynman_line(entry: dict[str, str]) -> str:
    return (
        _first_sentence(entry["feynman"])
        or _first_sentence(entry["principle"])
        or _first_sentence(entry["gap"])
        or _first_sentence(entry["what_broke"])
        or entry["title"]
    )


def digest(day: str) -> int:
    path = day_path(day)
    if not path.exists():
        print(f"missing: {path}")
        return 1
    text = path.read_text(encoding="utf-8")
    if "## Daily Digest" in text:
        print(f"daily digest already exists: {path}")
        return 0
    entries = parse_entries(text)
    if not entries:
        print(f"no entries: {path}")
        return 1

    counts = Counter(entry["category"] for entry in entries)
    surfaces = Counter(entry["surface"] for entry in entries if entry["surface"])
    for entry in entries:
        entry["date"] = day
        entry["pattern"] = _pattern_label(entry)
    pattern_counts = Counter(entry["pattern"] for entry in entries)
    ranked = sorted(entries, key=lambda entry: _entry_score(entry, pattern_counts), reverse=True)

    categories = ", ".join(f"{cat} ({count})" for cat, count in counts.most_common())
    surface_line = ", ".join(f"{surface} ({count})" for surface, count in surfaces.most_common()) or "unspecified"
    repeats = sorted(set(counts) & prior_categories(day))
    strongest = ranked[0]["principle"] or ranked[0]["title"]
    common_gap = next((entry["gap"] for entry in ranked if entry["gap"]), "No explicit gap captured.")
    guardrails = [entry["guardrail"] for entry in ranked if entry["guardrail"]]

    block = [
        "---",
        "",
        "## Daily Digest",
        "",
        f"**Entries today:** {len(entries)}",
        f"**Categories:** {categories}",
        f"**Surfaces:** {surface_line}",
        "",
        "### What you fixed",
        f"Logged {len(entries)} engineering learning entries across {len(counts)} categories.",
        "",
        "### What you learned",
        strongest,
        "",
        "### Your blind spot",
        common_gap,
        "",
        "### Explain it like I'm new (Feynman check)",
    ]
    for idx, entry in enumerate(ranked, start=1):
        block.append(f"{idx}. {entry['title']}: {_feynman_line(entry)}")

    block.extend(["", "### Guardrails to add"])
    if guardrails:
        block.extend(f"{idx}. {guardrail}" for idx, guardrail in enumerate(guardrails[:5], start=1))
    else:
        block.append("1. Add concrete guardrails to future entries.")

    block.extend(["", "### In the wild"])
    for entry in ranked[:3]:
        refs = _reference_bullets(entry)
        for ref in refs[:2]:
            block.append(f"- {entry['title']}: {ref}")

    block.extend(
        [
            "",
            "### Scorecard",
            "| Metric | Value |",
            "|---|---|",
            f"| Fixes logged | {len(entries)} |",
            f"| Categories hit | {', '.join(counts)} |",
            f"| Most frequent category | {counts.most_common(1)[0][0]} |",
            f"| Repeat categories from prior days | {', '.join(repeats) if repeats else 'none'} |",
            "",
            "### Review prompts consolidated",
        ]
    )
    for idx, entry in enumerate(ranked, start=1):
        question = entry["review_prompt"] or f"What principle did '{entry['title']}' teach?"
        answer = entry["review_answer"] or entry["principle"] or entry["guardrail"] or entry["title"]
        block.append(f"{idx}. {question}")
        block.append(f"   <details><summary>Answer</summary>{answer}</details>")

    block.extend(
        [
            "",
            "> Read these tomorrow morning. Answer from memory before checking.",
            "",
        ]
    )
    digest_text = "\n".join(block)
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n")
        fh.write(digest_text)
    print(path)
    print(digest_text)
    return 0


def _cluster_trend(entries: list[dict[str, str]]) -> str:
    days = sorted(_parse_day(entry["date"]) for entry in entries if entry.get("date"))
    days = [day for day in days if day is not None]
    if not days:
        return "stable"
    start = min(days)
    end = max(days)
    midpoint = date.fromordinal(start.toordinal() + (end.toordinal() - start.toordinal()) // 2)
    early = sum(1 for day in days if day <= midpoint)
    late = sum(1 for day in days if day > midpoint)
    if late > early:
        return "increasing"
    if late < early:
        return "decreasing"
    return "stable"


def _prior_retro_categories(current_file: str) -> set[str]:
    root = journal_dir(require_write=False)
    if not root.exists():
        return set()
    retros = sorted(
        (
            path
            for path in root.glob("retro-*.md")
            if RETRO_FILE_RE.match(path.name) and path.name != current_file
        ),
        reverse=True,
    )
    if not retros:
        return set()
    text = retros[0].read_text(encoding="utf-8")
    match = re.search(r"^\| Categories hit \| (.+?) \|$", text, re.MULTILINE)
    if not match:
        return set()
    cats: set[str] = set()
    for part in match.group(1).split(","):
        name = re.sub(r"\s*\(\d+\)$", "", part.strip())
        if name:
            cats.add(name)
    return cats


def _explain_entry(entry: dict[str, str]) -> str:
    mechanism = entry["gap"] or entry["principle"] or entry["title"]
    plain = entry["feynman"] or entry["principle"] or entry["tl_dr"] or entry["title"]
    real_bug = (
        _collapse(entry["evidence"])
        or _collapse(entry["what_broke"])
        or _collapse(entry["why_broke"])
        or entry["title"]
    )
    toy = entry["toy_example"] or "Strip the case down to the smallest input that still reproduces the wrong assumption."
    fuzzy = entry["fuzzy"] or entry["gap"] or "The explanation needs a sharper source-of-truth check."
    repair = (
        entry["guardrail"]
        or "Re-read the source of truth, make the assumption explicit, and encode the check in a repeatable guardrail."
    )
    principle = entry["principle"] or entry["title"]
    prediction = entry["prediction"] or f"What nearby scenario would break if '{entry['title']}' is still misunderstood?"
    prediction_answer = entry["prediction_answer"] or principle
    nearby = entry["nearby"] or entry["guardrail"] or "Apply the same check to the next similar workflow."

    lines = [
        f"# Feynman Re-Explanation - {entry['title']}",
        "",
        f"`{entry['category']}` · `{entry['impact'] or 'unspecified'}` · `{entry['surface'] or 'unspecified'}` · `{entry['date']}`",
        "",
        "1. Name the misunderstood mechanism",
        mechanism,
        "",
        "2. Explain it plainly",
        plain,
        "",
        "3. Tie it to the real bug",
        real_bug,
        "",
        "4. Create a toy example",
        toy,
        "",
        "5. Find the fuzzy part",
        fuzzy,
        "",
        "6. Repair the gap",
        repair,
        "",
        "7. State the transferable rule",
        principle,
        "",
        "8. Create a prediction check",
        prediction,
        f"<details><summary>Answer</summary>{prediction_answer}</details>",
        "",
        "9. Apply nearby",
        nearby,
    ]
    return "\n".join(lines)


def explain(title_query: str) -> int:
    query = title_query.strip().lower()
    if not query:
        print("missing title query")
        return 1

    exact: list[dict[str, str]] = []
    fuzzy: list[dict[str, str]] = []
    for path in all_day_paths():
        for entry in parse_entries(path.read_text(encoding="utf-8")):
            entry["date"] = path.stem
            title = entry["title"].strip().lower()
            if title == query:
                exact.append(entry)
            elif query in title:
                fuzzy.append(entry)

    matches = exact or fuzzy
    if not matches:
        print(f"missing entry: {title_query}")
        return 1

    selected = matches[0]
    print(_explain_entry(selected))
    return 0


def retro(limit_days: int, force: bool = False, save: bool = True) -> int:
    paths = recent_paths(limit_days)
    if len(paths) < 2:
        print("not enough data for a meaningful retro; use digest/review for a single day")
        return 1

    entries: list[dict[str, str]] = []
    for path in paths:
        for entry in parse_entries(path.read_text(encoding="utf-8")):
            entry["date"] = path.stem
            entry["pattern"] = _pattern_label(entry)
            entries.append(entry)
    if not entries:
        print("no recent entries")
        return 1

    pattern_groups: dict[str, list[dict[str, str]]] = {}
    for entry in entries:
        pattern_groups.setdefault(entry["pattern"], []).append(entry)

    pattern_sizes = {pattern: len(group) for pattern, group in pattern_groups.items()}
    ranked = sorted(entries, key=lambda entry: _entry_score(entry, pattern_sizes), reverse=True)
    top_entries = ranked[:5]

    category_counts = Counter(entry["category"] for entry in entries)
    pattern_counts = Counter(entry["pattern"] for entry in entries)
    start_day = min(path.stem for path in paths)
    end_day = max(path.stem for path in paths)
    retro_day = date.today().isoformat()
    path = retro_path(retro_day, require_write=save)

    if save and path.exists() and not force:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print(f"retro already exists: {path}")
            return 1
        response = input(f"Retro already exists at {path}. Overwrite? (yes / no)\n> ").strip().lower()
        if response not in {"y", "yes"}:
            print("retro not overwritten")
            return 1

    lines = [
        f"# Weekly Retrospective - {retro_day}",
        f"> Covering {limit_days} days: {start_day} to {end_day} | {len(entries)} entries across {len(paths)} sessions",
        "",
        "---",
        "",
        "## Pattern Clusters",
        "",
    ]

    repeated_patterns = [(pattern, group) for pattern, group in pattern_groups.items() if len(group) >= 2]
    for pattern, group in sorted(repeated_patterns, key=lambda item: len(item[1]), reverse=True):
        reps = sorted(group, key=lambda entry: _entry_score(entry, pattern_sizes), reverse=True)[:2]
        dates = sorted({entry["date"] for entry in group})
        dominant_gap = next((entry["gap"] for entry in reps if entry["gap"]), "The same assumption kept resurfacing in different forms.")
        lines.extend(
            [
                f"### Cluster: {pattern} ({len(group)} entries)",
                f"**Trend:** {_cluster_trend(group)}",
                f"**Dates:** {', '.join(dates)}",
                f"**The pattern:** {dominant_gap}",
                "**Representative entries:**",
            ]
        )
        for rep in reps:
            summary = _first_sentence(rep["gap"] or rep["principle"] or rep["title"])
            lines.append(f"- {rep['date']} - {rep['title']}: {summary}")
        lines.extend(
            [
                "",
                "**Evidence:**",
            ]
        )
        for ref in _reference_bullets(reps[0])[:3]:
            lines.append(f"- {ref}")
        lines.append("")

    if not repeated_patterns:
        lines.extend(
            [
                "Too early to tell - need more repeated patterns before clustering adds value.",
                "",
            ]
        )

    lines.extend(["---", "", "## Top 5 Critical Lessons", ""])
    for idx, entry in enumerate(top_entries, start=1):
        lines.extend(
            [
                f"#### {idx}. {entry['title']} ({entry['date']})",
                f"`{entry['category']}` · `{entry['pattern']}`",
                "",
                f"**The lesson in one line:** {entry['principle'] or entry['title']}",
                f"**Feynman explanation:** {_feynman_line(entry)}",
                f"**Why it matters:** Repeating this mistake recreates {entry['impact'] or 'engineering'} risk in a nearby workflow.",
                f"**Your trigger:** Remember this when you are about to rely on {_first_sentence(entry['gap'] or entry['title']).lower()}",
                f"**Guardrail:** {entry['guardrail'] or 'Add a concrete guardrail before the next similar change.'}",
                "",
                "**Evidence from the field:**",
            ]
        )
        for ref in _reference_bullets(entry)[:3]:
            lines.append(f"- {ref}")
        lines.append("")

    first_half_cutoff = len(paths) // 2
    later_days = {path.stem for path in paths[:first_half_cutoff]}
    earlier_days = {path.stem for path in paths[first_half_cutoff:]}
    earlier_patterns = {entry["pattern"] for entry in entries if entry["date"] in earlier_days}
    later_patterns = {entry["pattern"] for entry in entries if entry["date"] in later_days}
    stuck = sorted(earlier_patterns - later_patterns)
    repeated = sorted(earlier_patterns & later_patterns)

    previous_categories = _prior_retro_categories(path.name)
    current_categories = set(category_counts)
    new_categories = sorted(current_categories - previous_categories)
    resolved_categories = sorted(previous_categories - current_categories)

    lines.extend(
        [
            "---",
            "",
            "## Lessons That Stuck",
        ]
    )
    if stuck:
        lines.extend(f"- {pattern}" for pattern in stuck)
    else:
        lines.append("Too early to tell - need more data points.")

    lines.extend(["", "## Lessons That Didn't"])
    if repeated:
        lines.extend(f"- {pattern}" for pattern in repeated)
    else:
        lines.append("No repeat patterns detected - strong retention this period.")

    top_pattern, top_pattern_count = pattern_counts.most_common(1)[0]
    top_category, top_category_count = category_counts.most_common(1)[0]
    category_line = ", ".join(f"{cat} ({count})" for cat, count in category_counts.most_common())

    lines.extend(
        [
            "",
            "---",
            "",
            "## Trend Analysis",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| Total entries | {len(entries)} |",
            f"| Days active | {len(paths)} of {limit_days} |",
            f"| Categories hit | {category_line} |",
            f"| Most frequent category | {top_category} ({top_category_count} entries, {round(top_category_count * 100 / len(entries))}%) |",
            f"| Most frequent pattern | {top_pattern} ({top_pattern_count} entries) |",
            f"| New categories (not in prior retros) | {', '.join(new_categories) if new_categories else 'none'} |",
            f"| Resolved categories (in prior retros, not this one) | {', '.join(resolved_categories) if resolved_categories else 'none'} |",
            "",
            "## Guardrails To Implement Next",
        ]
    )
    guardrails = [entry["guardrail"] for entry in top_entries if entry["guardrail"]]
    if guardrails:
        for idx, guardrail in enumerate(guardrails[:3], start=1):
            lines.append(f"1. **{guardrail}** - prevents drift from recent repeat patterns." if idx == 1 else f"{idx}. **{guardrail}** - prevents drift from recent repeat patterns.")
    else:
        lines.append("1. **Add explicit guardrails to the next three entries** - prevents insights from staying abstract.")

    lines.extend(["", "## Focus Areas for Next Week"])
    focus_areas = repeated[:3] or [top_pattern]
    for idx, area in enumerate(focus_areas, start=1):
        lines.append(f"{idx}. **{area}** - verify this assumption earlier, before implementation starts.")

    lines.extend(
        [
            "",
            "## Active Recall Prompts",
            "",
            "> *Read these at the start of each day next week. Answer from memory, then expand to check.*",
            "",
        ]
    )
    for idx, entry in enumerate(top_entries, start=1):
        question = entry["review_prompt"] or f"What principle from '{entry['title']}' should you recall before a similar change?"
        answer = entry["review_answer"] or entry["principle"] or entry["guardrail"] or entry["title"]
        lines.append(f"{idx}. {question}")
        lines.append(f"   <details><summary>Answer</summary>{answer}</details>")

    retro_text = "\n".join(lines) + "\n"
    if save:
        path.write_text(retro_text, encoding="utf-8")
        print(f"Retro saved to {path}")
    print(retro_text.rstrip())
    return 0


def weekly(limit_days: int) -> int:
    return retro(limit_days, save=False)


def quiz(limit_days: int) -> int:
    entries = recent_entries(limit_days)
    if not entries:
        print("no review prompts found")
        return 1
    print("### Review Prompts")
    for idx, entry in enumerate(entries, start=1):
        question = entry["review_prompt"] or f"What principle did '{entry['title']}' teach?"
        answer = entry["review_answer"] or entry["principle"] or entry["guardrail"] or entry["title"]
        print(f"{idx}. {question}")
        print(f"   <details><summary>Answer</summary>{answer}</details>")
    predictions = [entry for entry in entries if entry["prediction"]]
    if predictions:
        print()
        print("### Prediction Checks")
        for idx, entry in enumerate(predictions, start=1):
            answer = entry["prediction_answer"] or entry["principle"] or entry["title"]
            print(f"{idx}. {entry['prediction']}")
            print(f"   <details><summary>Answer</summary>{answer}</details>")
    return 0


def gaps(limit_days: int) -> int:
    entries = recent_entries(limit_days)
    if not entries:
        print("no recent entries")
        return 1
    counts = Counter(entry["category"] for entry in entries)
    print("# Feynman Technique Gaps")
    print()
    print("## Repeat Categories")
    for category, count in counts.most_common():
        print(f"- {category}: {count}")
    print()
    print("## Mental-Model Gaps")
    for entry in entries:
        if entry["gap"]:
            print(f"- {entry['date']} / {entry['title']}: {_collapse(entry['gap'])}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Feynman Technique journal helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    append = sub.add_parser("append", help="append note from stdin")
    append.add_argument("--date", default=date.today().isoformat())
    append.add_argument("--title", required=True)

    dig = sub.add_parser("digest", help="append daily digest")
    dig.add_argument("--date", default=date.today().isoformat())

    ls = sub.add_parser("list", help="list entries for date")
    ls.add_argument("--date", default=date.today().isoformat())

    wk = sub.add_parser("weekly", help="legacy alias for retro output without saving")
    wk.add_argument("--limit", type=int, default=7)

    rt = sub.add_parser("retro", help="generate and save a retrospective from recent days")
    rt.add_argument("--limit", type=int, default=7)
    rt.add_argument("--force", action="store_true")

    qz = sub.add_parser("quiz", help="print active-recall prompts from recent entries")
    qz.add_argument("--limit", type=int, default=7)

    ex = sub.add_parser("explain", help="re-explain a journal entry by title")
    ex.add_argument("--title", required=True)

    gp = sub.add_parser("gaps", help="print repeated categories and gaps")
    gp.add_argument("--limit", type=int, default=7)

    args = parser.parse_args()
    if args.cmd == "append":
        return append_entry(args.date, args.title, sys.stdin.read())
    if args.cmd == "digest":
        return digest(args.date)
    if args.cmd == "list":
        return list_entries(args.date)
    if args.cmd == "weekly":
        return weekly(args.limit)
    if args.cmd == "retro":
        return retro(args.limit, force=args.force)
    if args.cmd == "quiz":
        return quiz(args.limit)
    if args.cmd == "explain":
        return explain(args.title)
    if args.cmd == "gaps":
        return gaps(args.limit)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
