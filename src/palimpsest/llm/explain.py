"""Grounded explanation of an analysis result with the Claude API (falls back to retrieved text offline)."""
import os

from ..config import KNOWLEDGE_FILE, LLM_MODEL, SCRIPTS
from .retriever import Chunk, Retriever

SYSTEM = """You are an assistant for archaeologists and epigraphers.
Rules:
- Ground historical claims in the provided REFERENCE notes; if they don't cover something, say so rather than guess.
- The script identification and transcription come from automated models and may be wrong. State confidence
  plainly and recommend expert verification. Never present a translation as certain, and never invent readings
  for signs that were not transcribed.
- Do not speculate about find-spot coordinates, and do not advise on locating or excavating sites.
- Be concise: what it likely is, historical context, what an expert should check next."""


def build_prompt(detections: list[str], script_scores: dict[str, float], transcription: str | None,
                 context: list[Chunk]) -> str:
    top = list(script_scores.items())[:3]
    scripts = "\n".join(f"- {SCRIPTS[k].name}: {p:.0%}" for k, p in top)
    refs = "\n\n".join(f"[{c.source}]\n{c.text}" for c in context) or "(no reference notes matched)"
    return (f"DETECTED OBJECTS:\n{', '.join(detections) or 'none'}\n\n"
            f"SCRIPT CANDIDATES (model estimate):\n{scripts}\n\n"
            f"MACHINE TRANSCRIPTION:\n{transcription or '(none available for this script)'}\n\n"
            f"REFERENCE NOTES:\n{refs}\n\nExplain this item for an archaeologist.")


def explain(detections: list[str], script_scores: dict[str, float], transcription: str | None,
            retriever: Retriever | None = None) -> str:
    retriever = retriever or Retriever()
    best = next(iter(script_scores), None)
    query = " ".join([SCRIPTS[best].name if best else "", *detections])
    context = retriever.search(query, boost_source=KNOWLEDGE_FILE.get(best))
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "ANTHROPIC_API_KEY not set — showing reference notes only.\n\n" + \
               "\n\n".join(c.text for c in context[:2])
    import anthropic
    msg = anthropic.Anthropic().messages.create(
        model=LLM_MODEL, max_tokens=1200, system=SYSTEM,
        messages=[{"role": "user", "content": build_prompt(detections, script_scores, transcription, context)}])
    return "".join(b.text for b in msg.content if b.type == "text")
