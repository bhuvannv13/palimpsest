# Palimpsest

Open-source toolkit that helps archaeologists triage photos of finds: **detect** artifacts and inscribed regions, **identify** the script, **transcribe** where feasible, and **explain** the history using an LLM grounded in a cited knowledge base.

```
photo ─► detector ─► script ID ─► OCR / sign reader ─► LLM + history notes (RAG) ─► report
         (OWLv2 /     (CLIP /      (Tesseract /          (Claude API, cites
          DETR)        ViT)         TrOCR)                knowledge/*.md)
```

## Honest scope
- Works out of the box (zero-shot): object detection, script identification, history explanations.
- Works for print-like Greek, Latin, Hebrew, Devanagari via Tesseract; weak on ancient hands until you fine-tune.
- **Not solved:** reliable reading of cuneiform, hieroglyphs, Linear B, runes, ogham. That needs a sign detector trained on annotated data (see `docs/TRAINING.md`). The tool reports candidates and confidence; it never claims a finished translation.
- Outputs are research aids. An epigraphist must verify.

## Quick start
```bash
pip install -e ".[all]"
# Tesseract binary + language packs (grc, lat, heb, san) for OCR
export ANTHROPIC_API_KEY=...        # optional; without it you get the reference notes only
palimpsest analyze photo.jpg
palimpsest app                      # Gradio UI
```

## Legal-safe data
```bash
python -m palimpsest.data.collect --source met --query cuneiform --limit 100 --download
```
Only CC0 / public domain / CC BY items pass the allow-list; each gets a provenance row and generated `ATTRIBUTION.md`. Images are not committed — the manifest is. Details and source status: [docs/DATA_POLICY.md](docs/DATA_POLICY.md).

## Responsible use
- Uploads are processed in memory; EXIF/GPS is stripped. Never publish find-spot coordinates.
- Don't use this to locate unprotected sites or trade in antiquities.
- Flag items from living communities or sacred contexts for human review.

## Extend
- Add a script: entry in `config.SCRIPTS`, `config.KNOWLEDGE_FILE`, and a cited note in `knowledge/`.
- Add a source: a generator in `data/collect.py` yielding `Record`s; record its terms in `docs/DATA_POLICY.md` first.
- Knowledge notes should cite scholarly sources; PRs with corrections from specialists are very welcome.

## Dev
```bash
pip install -e ".[dev]" && pytest
```
Code is MIT. Dataset licenses follow each item's manifest row.

## More
- [Contributing](CONTRIBUTING.md) · [Data policy](docs/DATA_POLICY.md) · [Training](docs/TRAINING.md) · [Model card template](docs/MODEL_CARD.md)
- Train a script classifier: `python -m palimpsest.training.train_script_classifier data/labeled`
- Docker: `docker build -t palimpsest . && docker run -p 7860:7860 -e ANTHROPIC_API_KEY palimpsest`
