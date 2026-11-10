# Data policy — how we avoid legal problems

**This is engineering practice, not legal advice.** Have counsel review before releasing a dataset or model commercially.

## Rules
1. **Allow-list, not block-list.** Only CC0, Public Domain Mark/PD, and CC BY images enter the manifest (`src/palimpsest/data/license.py`). Unknown, NC, ND and (by default) SA licenses are rejected. Add `--allow cc-by-sa` only if you accept share-alike obligations on the dataset.
2. **Per-item provenance.** Every image has a row in `manifest.jsonl` (source, URL, license, attribution, SHA-256, retrieval time). `ATTRIBUTION.md` is generated from it.
3. **Official APIs only; no scraping.** Collectors use documented public APIs with a descriptive User-Agent and rate-limiting. Respect each site's terms and `robots.txt`.
4. **Don't redistribute images unless the license permits it.** The repo ships the manifest and download scripts, not the images (`data/raw/images/` is git-ignored). Anyone can rebuild the dataset.
5. **Check the item, not the museum.** A museum's "open access" statement can exclude certain items; photographs of 3D objects can carry a photographer's copyright even when the object is ancient. The collectors read the per-item field; spot-check regularly.
6. **Cultural heritage and sovereignty.** Exclude items with community restrictions (e.g. Traditional Knowledge labels, sacred or sensitive material) even when openly licensed. Remove any item on request via an issue.
7. **No find-spot data.** Strip EXIF/GPS (the pipeline does this on every upload) and never publish site coordinates; precise locations help looters.
8. **Model licenses.** Dependencies used by default: OWLv2 (Apache-2.0), CLIP (MIT), TrOCR (MIT), Tesseract (Apache-2.0). Ultralytics YOLO is AGPL-3.0 and is deliberately **not** a dependency; if you add it, your combined work inherits AGPL terms.

## Source status
| Source | Status | License on items | Notes |
|---|---|---|---|
| Metropolitan Museum Open Access | Implemented | CC0 | Filtered by `isPublicDomain` |
| Cleveland Museum of Art Open Access | Implemented | CC0 | Filtered by `share_license_status` |
| Wikimedia Commons | Implemented | Per file | Allow-list checked per file; attribution kept |
| Smithsonian Open Access, Europeana, Wellcome, Library of Congress, Internet Archive | Planned | Varies | Needs API key and/or per-item rights check |
| CDLI, ORACC, Papyri.info, Perseus/Open Greek and Latin, DCS | Planned (text/transliteration) | Varies | Confirm each project's current license and any image restrictions before ingesting |

"Planned" sources must have their terms read and recorded here before a collector is merged.
