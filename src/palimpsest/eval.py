"""Metrics for model cards: OCR character error rate and script top-k accuracy."""


def cer(reference: str, hypothesis: str) -> float:
    """Character error rate = Levenshtein distance / len(reference)."""
    if not reference:
        return float(bool(hypothesis))
    prev = list(range(len(hypothesis) + 1))
    for i, rc in enumerate(reference, 1):
        cur = [i]
        for j, hc in enumerate(hypothesis, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (rc != hc)))
        prev = cur
    return prev[-1] / len(reference)


def top_k_accuracy(predictions: list[dict[str, float]], labels: list[str], k: int = 1) -> float:
    """predictions: per-image {label: score} dicts."""
    hits = sum(label in sorted(p, key=p.get, reverse=True)[:k] for p, label in zip(predictions, labels))
    return hits / len(labels) if labels else 0.0
