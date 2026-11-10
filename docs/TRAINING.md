# Training guide

Zero-shot models give a working baseline. Accuracy on real finds needs fine-tuning on expert-labelled data.

## 1. Build the dataset
```bash
python -m palimpsest.data.collect --source met --query cuneiform --limit 200 --download
python -m palimpsest.data.collect --source cleveland --query "inscribed tablet" --limit 100 --download
python -m palimpsest.data.collect --source commons --query "Linear B tablet" --limit 100 --download
```
Then label with an annotation tool (CVAT, Label Studio) exporting COCO format. Have an epigraphist review a sample.

## 2. Detector (Apache-2.0 route)
Fine-tune `PekingU/rtdetr_r50vd` or `facebook/detr-resnet-50` following the Hugging Face "Object detection" task guide, with classes such as `tablet`, `inscription`, `manuscript_page`, `papyrus`, `pottery_sherd`, `coin`, `seal`. Then:
```bash
palimpsest analyze photo.jpg --detector path/to/checkpoint
```
Split train/val **by object or site, not by photo**, or the metrics will be inflated by near-duplicate views.

## 3. Script classifier
Fine-tune `google/vit-base-patch16-224` (or ConvNeXt) with one label per key in `config.SCRIPTS`. Pass `--classifier path/to/checkpoint`.

## 4. Transcription
- Greek/Latin/Hebrew/Sanskrit manuscripts: fine-tune TrOCR on line crops with ground truth from open HTR datasets (check each dataset's license first).
- Cuneiform, hieroglyphs, Linear B: train a **sign detector** (one class per sign) on annotated sign images, then map to transliteration with a lookup table. Output candidates with confidence; do not auto-translate.

## 5. Evaluate
Report per-script precision/recall, character error rate for OCR, and failure analysis on damaged/worn items. Put results in a model card.
