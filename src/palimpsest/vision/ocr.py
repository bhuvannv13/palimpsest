"""Transcription backends.

- Tesseract: usable for Greek, Latin, Hebrew, Sanskrit print and clean manuscripts. Weak on ancient hands.
- TrOCR: plug in your own fine-tuned line-level checkpoint (handwritten/manuscript lines).
- Cuneiform, hieroglyphs, Linear B, runes, ogham, oracle bone have no reliable off-the-shelf OCR; for these
  train a sign detector on licensed sign data and return transliteration candidates, never a finished translation.
"""
from dataclasses import dataclass

from PIL import Image

from ..config import SCRIPTS


@dataclass
class Transcription:
    text: str
    confidence: float  # 0-1, mean token confidence; 0 when unavailable
    backend: str


def tesseract(image: Image.Image, script_key: str) -> Transcription | None:
    lang = SCRIPTS[script_key].tesseract_lang
    if not lang:
        return None
    import pytesseract
    data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
    words = [(w, float(c)) for w, c in zip(data["text"], data["conf"]) if w.strip() and float(c) >= 0]
    if not words:
        return Transcription("", 0.0, f"tesseract:{lang}")
    return Transcription(" ".join(w for w, _ in words), sum(c for _, c in words) / len(words) / 100,
                         f"tesseract:{lang}")


class TrOCRReader:
    def __init__(self, checkpoint: str):
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        self.processor = TrOCRProcessor.from_pretrained(checkpoint)
        self.model = VisionEncoderDecoderModel.from_pretrained(checkpoint).eval()

    def __call__(self, line_image: Image.Image) -> Transcription:
        pixel = self.processor(images=line_image.convert("RGB"), return_tensors="pt").pixel_values
        ids = self.model.generate(pixel, max_new_tokens=128)
        return Transcription(self.processor.batch_decode(ids, skip_special_tokens=True)[0], 0.0, "trocr")


def transcribe(image: Image.Image, script_key: str, trocr: TrOCRReader | None = None) -> Transcription | None:
    if trocr:
        return trocr(image)
    return tesseract(image, script_key)
