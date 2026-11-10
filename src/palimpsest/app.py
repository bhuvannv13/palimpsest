"""Gradio front-end. Uploaded images are processed in memory and never stored."""
from PIL import ImageDraw

from .config import SCRIPTS


def launch():
    import gradio as gr

    from .cli import build_pipeline
    pipe = build_pipeline()

    def run(image):
        res = pipe(image)
        annotated = image.convert("RGB")
        draw = ImageDraw.Draw(annotated)
        for d in res.detections[:8]:
            draw.rectangle(d.box, outline="red", width=3)
            draw.text((d.box[0] + 4, d.box[1] + 4), f"{d.label} {d.score:.2f}", fill="red")
        scripts = {SCRIPTS[k].name: v for k, v in list(res.script_scores.items())[:5]}
        text = res.transcription.text if res.transcription else "(no OCR available for this script)"
        return annotated, scripts, text, res.explanation

    gr.Interface(
        run, gr.Image(type="pil", label="Photo of artifact or manuscript"),
        [gr.Image(label="Detections"), gr.Label(label="Script candidates"),
         gr.Textbox(label="Machine transcription (unverified)"), gr.Markdown(label="Explanation")],
        title="Palimpsest", description="Research aid only — outputs are model estimates. Verify with an expert.",
        allow_flagging="never").launch()
