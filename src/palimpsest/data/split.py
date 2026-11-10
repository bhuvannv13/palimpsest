"""Leak-free train/val/test splits: all photos of the same object land in the same split."""
import hashlib
import re

_VIEW = re.compile(r"[\s_\-]*(\d+|view|side|obverse|reverse|recto|verso|detail)\b.*$")


def group_key(title: str, fallback: str) -> str:
    """Normalise a title so 'Tablet 1.jpg' and 'Tablet 2.jpg' share a group."""
    base = re.sub(r"\.\w{3,4}$", "", title.lower())
    return _VIEW.sub("", base).strip() or fallback


def assign(group: str, val: float = 0.1, test: float = 0.1) -> str:
    """Deterministic split by hashing the group key."""
    x = int(hashlib.sha256(group.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "test" if x < test else "val" if x < test + val else "train"
