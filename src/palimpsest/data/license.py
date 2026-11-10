"""License normalisation and allow-listing. The gate every collected image must pass."""
import re

# Default: only licenses that permit training and redistribution with at most attribution.
DEFAULT_ALLOWED = frozenset({"cc0", "pdm", "cc-by"})


def normalize(raw: str | None) -> str | None:
    """Map free-text license strings to a canonical key, or None if unrecognised."""
    if not raw:
        return None
    s = re.sub(r"\s+", "-", raw.strip().lower().replace("_", "-"))
    if "-nc" in s or "-nd" in s:
        return "non-open"
    if s in {"cc0", "cc0-1.0", "cc-zero"} or s.startswith("cc0-"):
        return "cc0"
    if s.startswith("cc-by-sa"):
        return "cc-by-sa"
    if s.startswith("cc-by"):
        return "cc-by"
    if s in {"public-domain", "pd", "pdm", "public-domain-mark", "pdm-1.0"} or s.startswith("pd-"):
        return "pdm"
    return None


def is_allowed(raw: str | None, allowed: frozenset[str] = DEFAULT_ALLOWED) -> bool:
    return normalize(raw) in allowed
