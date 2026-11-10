"""Tiny TF-IDF retriever over knowledge/*.md so the LLM explains from curated, cited text."""
import re
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..config import KNOWLEDGE_DIR


@dataclass
class Chunk:
    source: str  # file stem, e.g. "cuneiform"
    text: str


def load_chunks(directory: Path = KNOWLEDGE_DIR) -> list[Chunk]:
    chunks = []
    for path in sorted(directory.glob("*.md")):
        for part in re.split(r"\n(?=## )", path.read_text(encoding="utf-8")):
            if part.strip():
                chunks.append(Chunk(path.stem, part.strip()))
    return chunks


class Retriever:
    def __init__(self, chunks: list[Chunk] | None = None):
        self.chunks = chunks if chunks is not None else load_chunks()
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vec.fit_transform([c.text for c in self.chunks]) if self.chunks else None

    def search(self, query: str, k=4, boost_source: str | None = None) -> list[Chunk]:
        if not self.chunks:
            return []
        sims = cosine_similarity(self.vec.transform([query]), self.matrix)[0]
        if boost_source:
            sims = sims + [0.5 if c.source == boost_source else 0 for c in self.chunks]
        order = sims.argsort()[::-1][:k]
        return [self.chunks[i] for i in order if sims[i] > 0]
