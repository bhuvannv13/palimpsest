"""Fine-tune an image classifier for script identification.

Expects data_dir/<script_key>/*.jpg where <script_key> is a key from config.SCRIPTS.
    python -m palimpsest.training.train_script_classifier data/labeled --out runs/script_vit
"""
import argparse
from pathlib import Path

from PIL import Image

from ..data.split import assign, group_key


def main(argv=None):
    import numpy as np
    import torch
    from transformers import AutoImageProcessor, AutoModelForImageClassification, Trainer, TrainingArguments

    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir", type=Path)
    ap.add_argument("--out", type=Path, default=Path("runs/script_vit"))
    ap.add_argument("--base", default="google/vit-base-patch16-224")
    ap.add_argument("--epochs", type=int, default=5)
    args = ap.parse_args(argv)

    labels = sorted(d.name for d in args.data_dir.iterdir() if d.is_dir())
    files = [(p, labels.index(d)) for d in labels for p in sorted((args.data_dir / d).glob("*.jp*g"))]
    proc = AutoImageProcessor.from_pretrained(args.base)

    class DS(torch.utils.data.Dataset):
        def __init__(self, items):
            self.items = items

        def __len__(self):
            return len(self.items)

        def __getitem__(self, i):
            p, y = self.items[i]
            px = proc(Image.open(p).convert("RGB"), return_tensors="pt")["pixel_values"][0]
            return {"pixel_values": px, "labels": y}

    split = {s: [] for s in ("train", "val", "test")}
    for p, y in files:
        split[assign(group_key(p.stem, p.stem))].append((p, y))
    print({k: len(v) for k, v in split.items()})

    model = AutoModelForImageClassification.from_pretrained(
        args.base, num_labels=len(labels), id2label=dict(enumerate(labels)),
        label2id={l: i for i, l in enumerate(labels)}, ignore_mismatched_sizes=True)
    trainer = Trainer(
        model=model, train_dataset=DS(split["train"]), eval_dataset=DS(split["val"]),
        args=TrainingArguments(str(args.out), num_train_epochs=args.epochs, per_device_train_batch_size=16,
                               eval_strategy="epoch", remove_unused_columns=False, report_to="none"),
        compute_metrics=lambda ep: {"accuracy": float((np.argmax(ep.predictions, -1) == ep.label_ids).mean())})
    trainer.train()
    trainer.save_model(str(args.out))
    proc.save_pretrained(str(args.out))
    print("test:", trainer.evaluate(DS(split["test"]), metric_key_prefix="test"))


if __name__ == "__main__":
    main()
