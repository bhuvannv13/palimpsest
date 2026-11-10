"""Artifact / inscription detection.

ZeroShotDetector (OWLv2, Apache-2.0) works with no training data.
FineTunedDetector loads any Hugging Face object-detection checkpoint (DETR / RT-DETR, Apache-2.0)
that you fine-tune on the license-clean dataset built by `palimpsest.data.collect`.
"""
from dataclasses import dataclass

from PIL import Image

from ..config import DETECTOR_QUERIES


@dataclass
class Detection:
    label: str
    score: float
    box: tuple[int, int, int, int]  # x0, y0, x1, y1 in pixels

    def crop(self, image: Image.Image) -> Image.Image:
        return image.crop(self.box)


class ZeroShotDetector:
    def __init__(self, queries=DETECTOR_QUERIES, threshold=0.15, model_id="google/owlv2-base-patch16-ensemble"):
        import torch
        from transformers import Owlv2ForObjectDetection, Owlv2Processor
        self.torch, self.queries, self.threshold = torch, list(queries), threshold
        self.processor = Owlv2Processor.from_pretrained(model_id)
        self.model = Owlv2ForObjectDetection.from_pretrained(model_id).eval()

    def __call__(self, image: Image.Image) -> list[Detection]:
        inputs = self.processor(text=[self.queries], images=image, return_tensors="pt")
        with self.torch.no_grad():
            out = self.model(**inputs)
        side = max(image.size)  # OWLv2 pads to a square
        res = self.processor.post_process_object_detection(
            out, threshold=self.threshold, target_sizes=self.torch.tensor([[side, side]]))[0]
        w, h = image.size
        dets = []
        for score, label, box in zip(res["scores"], res["labels"], res["boxes"]):
            x0, y0, x1, y1 = (int(v) for v in box.tolist())
            dets.append(Detection(self.queries[int(label)], float(score),
                                  (max(x0, 0), max(y0, 0), min(x1, w), min(y1, h))))
        return sorted(dets, key=lambda d: -d.score)


class FineTunedDetector:
    def __init__(self, checkpoint: str, threshold=0.3):
        from transformers import pipeline
        self.pipe = pipeline("object-detection", model=checkpoint)
        self.threshold = threshold

    def __call__(self, image: Image.Image) -> list[Detection]:
        return [Detection(r["label"], r["score"],
                          tuple(int(r["box"][k]) for k in ("xmin", "ymin", "xmax", "ymax")))
                for r in self.pipe(image, threshold=self.threshold)]
