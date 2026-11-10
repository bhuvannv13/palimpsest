# Contributing

Thanks for helping. Three kinds of contribution matter most:

1. **Expert corrections** to `knowledge/*.md`. Cite a scholarly source for every claim.
2. **New scripts**: add an entry to `config.SCRIPTS` and `config.KNOWLEDGE_FILE`, plus a cited note. `tests/test_core.py` enforces that every script has a note.
3. **New data sources**: read the source's terms first and record them in `docs/DATA_POLICY.md`. Collectors must yield only items whose per-item license passes `data/license.py`. No scraping outside official APIs.

## Rules
- Run `pytest` before opening a PR.
- Never commit images, model weights, API keys, or find-spot coordinates.
- Outputs must stay hedged: no feature may present a machine reading as a verified translation.

## Reporting a rights or heritage concern
Open a "Takedown / heritage concern" issue. Items are removed from the manifest on request, no questions asked.
