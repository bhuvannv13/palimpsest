import json

from palimpsest.data import manifest
from palimpsest.data.license import is_allowed, normalize
from palimpsest.llm.explain import build_prompt
from palimpsest.llm.retriever import Retriever
from palimpsest.config import KNOWLEDGE_FILE, SCRIPTS


def test_license_normalisation():
    assert normalize("CC0 1.0") == "cc0"
    assert normalize("CC BY 4.0") == "cc-by"
    assert normalize("CC BY-SA 4.0") == "cc-by-sa"
    assert normalize("CC BY-NC 4.0") == "non-open"
    assert normalize("CC BY-ND 2.0") == "non-open"
    assert normalize("Public domain") == "pdm"
    assert normalize("PD-old-70") == "pdm"
    assert normalize("All rights reserved") is None


def test_default_allowlist_excludes_sharealike_and_nc():
    assert is_allowed("CC0") and is_allowed("Public domain") and is_allowed("CC BY 4.0")
    assert not is_allowed("CC BY-SA 4.0")
    assert not is_allowed("CC BY-NC 4.0")
    assert not is_allowed(None)


def test_manifest_dedupes_and_attributes(tmp_path):
    p = tmp_path / "manifest.jsonl"
    r = manifest.Record("met", "1", "Tablet", "http://i", "http://p", "cc0", "Gift of X")
    assert manifest.append(p, [r]) == 1
    assert manifest.append(p, [r]) == 0
    manifest.write_attribution(p, tmp_path / "ATTRIBUTION.md")
    assert "Tablet" in (tmp_path / "ATTRIBUTION.md").read_text()
    assert json.loads(p.read_text().splitlines()[0])["license"] == "cc0"


def test_retriever_finds_right_note():
    r = Retriever()
    assert r.search("Rosetta Stone Champollion decipherment")[0].source == "egyptian_hieroglyphs"
    assert r.search("wedge-shaped clay tablet Mesopotamia")[0].source == "cuneiform"


def test_every_script_has_a_knowledge_file():
    sources = {c.source for c in Retriever().chunks}
    assert set(KNOWLEDGE_FILE) == set(SCRIPTS)
    assert set(KNOWLEDGE_FILE.values()) <= sources


def test_prompt_contains_uncertainty_inputs():
    prompt = build_prompt(["a clay tablet"], {"cuneiform": 0.8, "linear_b": 0.1}, None, [])
    assert "Cuneiform: 80%" in prompt and "no reference notes" in prompt


def test_cer_and_topk():
    from palimpsest.eval import cer, top_k_accuracy
    assert cer("abc", "abc") == 0 and cer("abc", "abd") == 1 / 3 and cer("", "") == 0
    preds = [{"a": 0.6, "b": 0.4}, {"a": 0.3, "b": 0.7}]
    assert top_k_accuracy(preds, ["a", "a"], 1) == 0.5 and top_k_accuracy(preds, ["a", "a"], 2) == 1.0


def test_split_keeps_views_of_one_object_together():
    from palimpsest.data.split import assign, group_key
    assert group_key("Cuneiform Akkadian clay tablet 1.jpg", "x") == group_key("Cuneiform Akkadian clay tablet 2.jpg", "y")
    g = group_key("Tablet 7.jpg", "x")
    assert assign(g) == assign(g) and assign(g) in {"train", "val", "test"}
