# Model card (template)

Copy this for each released checkpoint.

- **Model**: base checkpoint + fine-tuning script + commit hash
- **Task**: detection / script ID / transcription
- **Training data**: manifest file and its SHA-256; licenses present; number of items per script
- **Split**: group-aware (`palimpsest.data.split`); state the test-set size
- **Metrics**: per-script top-1/top-3 (`palimpsest.eval.top_k_accuracy`); OCR CER (`palimpsest.eval.cer`); failure analysis on worn or fragmentary items
- **Known gaps**: scripts, periods and regions under-represented (museum open-access data skews towards well-known collections)
- **Intended use**: triage aid for specialists
- **Out of scope**: authentication of antiquities, valuation, locating sites, unsupervised translation

Baseline zero-shot models (OWLv2, CLIP) have **not** been benchmarked on this project's data; do not quote accuracy figures until you have run an evaluation.
