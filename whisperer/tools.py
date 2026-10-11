"""Tools the agent can call: a tiny local memory of the traps that catch you."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from strands import tool

DATA_FILE = Path(os.environ.get("WHISPERER_DATA_FILE", Path.home() / ".whisperer_mistakes.json"))


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _load() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # A corrupted file should never break a study session.
        return []


def _save(records: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


@tool
def log_mistake(topic: str, trap: str, domain: str = "General") -> str:
    """Save the trap that just caught the learner and say how many times it happened before.

    Args:
        topic: Short name of the concept, e.g. "RAG vs fine-tuning".
        trap: The confusion in a few words, e.g. "picked fine-tuning for fresh data".
        domain: Exam domain, e.g. "Applications of Foundation Models".
    """
    records = _load()
    key = _normalize(topic)
    previous = sum(1 for r in records if _normalize(r["topic"]) == key)
    records.append({
        "topic": topic.strip(),
        "trap": trap.strip(),
        "domain": domain.strip() or "General",
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    _save(records)
    if previous == 0:
        return f"First time the trap '{topic}' caught the learner."
    return f"The trap '{topic}' has caught the learner {previous} time(s) before. Mention it kindly."


@tool
def my_weak_spots(limit: int = 3) -> str:
    """Return the topics that caught the learner most often.

    Args:
        limit: How many topics to return.
    """
    records = _load()
    if not records:
        return "No traps logged yet."
    counts: dict[str, int] = {}
    names: dict[str, str] = {}
    for r in records:
        key = _normalize(r["topic"])
        counts[key] = counts.get(key, 0) + 1
        names.setdefault(key, r["topic"])
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return "\n".join(f"{names[k]}: {n}x" for k, n in ranked)


def weak_spots_report(limit: int = 5) -> str:
    """Plain (non-LLM) progress report used by the /progress command."""
    records = _load()
    if not records:
        return "📒 No traps logged yet. Paste a question you missed and let's start!"
    counts: dict[str, int] = {}
    names: dict[str, str] = {}
    for r in records:
        key = _normalize(r["topic"])
        counts[key] = counts.get(key, 0) + 1
        names.setdefault(key, r["topic"])
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    lines = [f"📒 Your recurring traps ({len(records)} logged):"]
    for key, n in ranked:
        bar = "●" * n
        lines.append(f"   {bar:<6} {names[key]} ({n}x)")
    return "\n".join(lines)
