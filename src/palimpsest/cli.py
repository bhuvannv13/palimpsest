import argparse
import sys

from PIL import Image


def build_pipeline(detector_ckpt=None, classifier_ckpt=None, use_llm=True):
    from .pipeline import Pipeline
    from .vision.detector import FineTunedDetector, ZeroShotDetector
    from .vision.script_id import ScriptClassifier
    detector = FineTunedDetector(detector_ckpt) if detector_ckpt else ZeroShotDetector()
    return Pipeline(detector, ScriptClassifier(classifier_ckpt), use_llm)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="palimpsest")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="analyze one image")
    a.add_argument("image")
    a.add_argument("--detector")
    a.add_argument("--classifier")
    a.add_argument("--no-llm", action="store_true")
    sub.add_parser("app", help="launch the Gradio web app")
    args = ap.parse_args(argv)

    if args.cmd == "app":
        from .app import launch
        return launch()

    result = build_pipeline(args.detector, args.classifier, not args.no_llm)(Image.open(args.image))
    print("Detections:")
    for d in result.detections[:8]:
        print(f"  {d.label}: {d.score:.2f} {d.box}")
    print("Script candidates:", {k: round(v, 2) for k, v in list(result.script_scores.items())[:3]})
    if result.transcription:
        print(f"Transcription [{result.transcription.backend}]: {result.transcription.text}")
    print("\n" + result.explanation)


if __name__ == "__main__":
    sys.exit(main())
