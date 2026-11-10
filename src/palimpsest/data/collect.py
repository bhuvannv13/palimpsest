"""License-gated collectors for open-access sources (no API keys needed).

Usage:
    python -m palimpsest.data.collect --source met --query cuneiform --limit 50 --download
"""
import argparse
import hashlib
import re
import time
from pathlib import Path

import requests

from . import manifest
from .license import DEFAULT_ALLOWED, is_allowed, normalize
from .manifest import Record

UA = "palimpsest-research/0.1 (open-source archaeology project; set PALIMPSEST_CONTACT in your fork)"
HEADERS = {"User-Agent": UA}
POLITE_DELAY = 0.2


def _get(url: str, **params):
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    time.sleep(POLITE_DELAY)
    return r


def met(query: str, limit: int, allowed=DEFAULT_ALLOWED):
    """Metropolitan Museum Open Access (CC0)."""
    base = "https://collectionapi.metmuseum.org/public/collection/v1"
    page = max(limit * 2, 20)  # over-fetch: some objects lack images
    ids = _get(f"{base.replace('/v1', '/v1.1')}/search", q=query, hasImages="true", isPublicDomain="true",
               limit=page, offset=0).json().get("objectIDs") or []
    for oid in ids:
        o = _get(f"{base}/objects/{oid}").json()
        if not o.get("isPublicDomain") or not o.get("primaryImageSmall"):
            continue
        yield Record("met", str(oid), o.get("title", ""), o["primaryImageSmall"], o.get("objectURL", ""),
                     "cc0", o.get("creditLine", ""), o.get("culture", ""), query)


def cleveland(query: str, limit: int, allowed=DEFAULT_ALLOWED):
    """Cleveland Museum of Art Open Access (CC0)."""
    data = _get("https://openaccess-api.clevelandart.org/api/artworks/",
                q=query, cc0=1, has_image=1, limit=limit).json().get("data", [])
    for a in data:
        img = (a.get("images") or {}).get("web", {}).get("url")
        if not img or a.get("share_license_status") != "CC0":
            continue
        yield Record("cleveland", str(a["id"]), a.get("title", ""), img, a.get("url", ""), "cc0",
                     a.get("creditline", ""), ", ".join(a.get("culture") or []), query)


def _strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "").strip()


def commons(query: str, limit: int, allowed=DEFAULT_ALLOWED):
    """Wikimedia Commons. Per-file license is read and checked; many files are CC BY-SA and are skipped by default."""
    data = _get("https://commons.wikimedia.org/w/api.php", action="query", format="json",
                generator="search", gsrsearch=f"{query} filetype:bitmap", gsrnamespace=6, gsrlimit=limit * 3,
                prop="imageinfo", iiprop="url|extmetadata|mime", iiurlwidth=1280).json()
    for p in (data.get("query", {}).get("pages", {})).values():
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        if info.get("mime") not in ("image/jpeg", "image/png") or not is_allowed(lic, allowed):
            continue
        yield Record("commons", str(p["pageid"]), p["title"].removeprefix("File:"),
                     info.get("thumburl") or info["url"], info.get("descriptionurl", ""),
                     normalize(lic), _strip_html(meta.get("Artist", {}).get("value", "")), "", query)


SOURCES = {"met": met, "cleveland": cleveland, "commons": commons}


def download(rec: Record, out_dir: Path) -> Record | None:
    r = requests.get(rec.image_url, headers=HEADERS, timeout=60)
    time.sleep(POLITE_DELAY)
    if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/"):
        return None
    path = out_dir / "images" / f"{rec.source}_{rec.source_id}.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(r.content)
    rec.sha256 = hashlib.sha256(r.content).hexdigest()
    rec.local_path = str(path)
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", choices=SOURCES, required=True)
    ap.add_argument("--query", required=True)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--out", type=Path, default=Path("data/raw"))
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--allow", nargs="*", default=sorted(DEFAULT_ALLOWED),
                    help="license keys to accept (add cc-by-sa only if you accept share-alike)")
    args = ap.parse_args(argv)

    allowed = frozenset(args.allow)
    recs = []
    for rec in SOURCES[args.source](args.query, args.limit, allowed):
        if rec.license not in allowed:
            continue
        if args.download and not (rec := download(rec, args.out)):
            continue
        recs.append(rec)
        if len(recs) >= args.limit:
            break
    added = manifest.append(args.out / "manifest.jsonl", recs)
    manifest.write_attribution(args.out / "manifest.jsonl", args.out / "ATTRIBUTION.md")
    print(f"{added} new records ({len(recs)} fetched) -> {args.out / 'manifest.jsonl'}")


if __name__ == "__main__":
    main()
