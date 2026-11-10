"""Script identification: zero-shot CLIP by default, or a fine-tuned image classifier."""
from PIL import Image

from ..config import SCRIPTS


class ScriptClassifier:
    def __init__(self, checkpoint: str | None = None, clip_id="openai/clip-vit-base-patch32"):
        import torch
        self.torch = torch
        self.keys = list(SCRIPTS)
        if checkpoint:  # fine-tuned ViT/ConvNeXt etc. whose id2label uses the keys in config.SCRIPTS
            from transformers import pipeline
            self.pipe = pipeline("image-classification", model=checkpoint, top_k=len(self.keys))
            self.clip = None
        else:
            from transformers import CLIPModel, CLIPProcessor
            self.pipe = None
            self.clip = CLIPModel.from_pretrained(clip_id).eval()
            self.proc = CLIPProcessor.from_pretrained(clip_id)

    def __call__(self, image: Image.Image) -> dict[str, float]:
        """Return {script_key: probability}, sorted high to low."""
        if self.pipe:
            scores = {r["label"]: r["score"] for r in self.pipe(image)}
        else:
            prompts = [f"a photo of {SCRIPTS[k].clip_prompt}" for k in self.keys]
            inputs = self.proc(text=prompts, images=image, return_tensors="pt", padding=True)
            with self.torch.no_grad():
                probs = self.clip(**inputs).logits_per_image.softmax(dim=-1)[0]
            scores = dict(zip(self.keys, probs.tolist()))
        return dict(sorted(scores.items(), key=lambda kv: -kv[1]))
