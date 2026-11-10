"""End-to-end: image -> detections -> script ID -> transcription -> grounded explanation."""
from dataclasses import dataclass, field

from PIL import Image

from .config import TEXT_BEARING
from .llm.explain import explain
from .vision.detector import Detection
from .vision.ocr import Transcription, transcribe


def sanitize(image: Image.Image) -> Image.Image:
    """Re-encode pixels only, dropping EXIF (incl. GPS) so find-spots never leak into logs or outputs."""
    clean = Image.new("RGB", image.size)
    clean.paste(image.convert("RGB"))
    return clean


@dataclass
class Analysis:
    detections: list[Detection] = field(default_factory=list)
    script_scores: dict[str, float] = field(default_factory=dict)
    transcription: Transcription | None = None
    explanation: str = ""


class Pipeline:
    def __init__(self, detector, classifier, use_llm=True):
        self.detector, self.classifier, self.use_llm = detector, classifier, use_llm

    def __call__(self, image: Image.Image) -> Analysis:
        image = sanitize(image)
        dets = self.detector(image)
        regions = [d for d in dets if any(t in d.label for t in TEXT_BEARING)]
        target = regions[0].crop(image) if regions else image
        scores = self.classifier(target)
        best = next(iter(scores))
        tr = transcribe(target, best)
        out = Analysis(dets, scores, tr)
        if self.use_llm:
            out.explanation = explain([d.label for d in dets[:5]], scores, tr.text if tr else None)
        return out
