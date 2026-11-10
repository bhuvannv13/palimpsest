"""Shared configuration: script catalogue, detector queries, paths."""
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = Path(os.getenv("PALIMPSEST_KNOWLEDGE", ROOT / "knowledge"))
LLM_MODEL = os.getenv("PALIMPSEST_MODEL", "claude-sonnet-5-5")


@dataclass(frozen=True)
class Script:
    key: str
    name: str
    clip_prompt: str  # description used for zero-shot identification
    tesseract_lang: str | None = None  # None = no usable off-the-shelf OCR


SCRIPTS: dict[str, Script] = {s.key: s for s in [
    Script("cuneiform", "Cuneiform", "wedge-shaped cuneiform writing pressed into a clay tablet"),
    Script("egyptian_hieroglyphs", "Egyptian hieroglyphs", "Egyptian hieroglyphs carved on stone or painted on papyrus"),
    Script("linear_b", "Linear B", "Linear B syllabic script on a clay tablet"),
    Script("greek", "Ancient Greek", "ancient Greek inscription or manuscript", "grc"),
    Script("latin", "Latin", "Roman Latin inscription or medieval Latin manuscript", "lat"),
    Script("brahmi", "Brahmi", "ancient Brahmi script inscription on stone", None),
    Script("sanskrit_devanagari", "Sanskrit (Devanagari)", "Sanskrit manuscript in Devanagari script", "san"),
    Script("hebrew", "Hebrew", "ancient Hebrew or Dead Sea Scroll manuscript", "heb"),
    Script("runic", "Runic", "runic inscription carved on a runestone", None),
    Script("ogham", "Ogham", "ogham inscription of notches along the edge of a standing stone", None),
    Script("oracle_bone", "Oracle-bone script", "Chinese oracle bone script on a bone or turtle shell", None),
]}

# Object classes the zero-shot detector looks for when no fine-tuned weights exist.
DETECTOR_QUERIES = [
    "a clay tablet with writing",
    "a stone inscription",
    "a manuscript page",
    "a papyrus fragment",
    "a palm-leaf manuscript",
    "a pottery sherd",
    "an ancient coin",
    "a cylinder seal",
    "a bone with carved writing",
]

# Region labels that likely contain writing and are worth sending to script ID / OCR.
TEXT_BEARING = ("tablet", "inscription", "manuscript", "papyrus", "bone", "palm-leaf", "seal")

# Which knowledge/*.md file covers each script (used to boost retrieval).
KNOWLEDGE_FILE = {
    "cuneiform": "cuneiform", "egyptian_hieroglyphs": "egyptian_hieroglyphs", "linear_b": "linear_b",
    "greek": "greek_latin", "latin": "greek_latin", "brahmi": "brahmi", "sanskrit_devanagari": "brahmi",
    "hebrew": "runic_ogham_oracle_hebrew", "runic": "runic_ogham_oracle_hebrew",
    "ogham": "runic_ogham_oracle_hebrew", "oracle_bone": "runic_ogham_oracle_hebrew",
}
