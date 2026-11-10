"""Provenance manifest: one JSONL row per image, plus a generated ATTRIBUTION.md."""
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Record:
    source: str
    source_id: str
    title: str
    image_url: str
    page_url: str
    license: str  # canonical key from license.normalize
    attribution: str = ""
    culture: str = ""
    query: str = ""
    sha256: str = ""
    local_path: str = ""
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))

    @property
    def key(self) -> tuple[str, str]:
        return (self.source, self.source_id)


def load(path: Path) -> list[Record]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [Record(**json.loads(line)) for line in f if line.strip()]


def append(path: Path, records: list[Record]) -> int:
    """Append records not already present (dedupe on source + source_id). Returns count added."""
    path.parent.mkdir(parents=True, exist_ok=True)
    seen = {r.key for r in load(path)}
    new = [r for r in records if r.key not in seen]
    with path.open("a", encoding="utf-8") as f:
        for r in new:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
    return len(new)


def write_attribution(manifest: Path, out: Path) -> None:
    lines = ["# Attribution", "", "Auto-generated from `manifest.jsonl`. Do not edit by hand.", ""]
    for r in load(manifest):
        credit = f" — {r.attribution}" if r.attribution else ""
        lines.append(f"- [{r.title or r.source_id}]({r.page_url}) ({r.source}, {r.license.upper()}){credit}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
