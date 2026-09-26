# ALAMA Audio Dataset

Short audio clips of Moroccan Arabic (Darija) speech from three cities —
**Casablanca**, **Oujda** and **Tangier** — each transcribed and labelled
independently by three annotators.

| | Casablanca | Oujda | Tangier | Total |
|---|---|---|---|---|
| Clips | 40 | 40 | 40 | **120** |
| Annotations (3 per clip) | 120 | 120 | 120 | **360** |

Audio is 16 kHz WAV, about 115 MB in total, stored with Git LFS.

> _TODO: a sentence or two on what the dataset is for (e.g. ASR for Moroccan
> dialects, dialect identification) and who made it._

## Layout

```
data/
  audio/
    casablanca/casablanca-001.wav … casablanca-040.wav
    oujda/oujda-001.wav … oujda-040.wav
    tangier/tangier-001.wav … tangier-041.wav   (no tangier-039, see Notes)
  metadata.csv            one row per clip
annotations/
  annotations.csv         one row per clip × annotator
scripts/
  restructure.py          one-off script that produced this layout
  validate.py             checks the dataset is complete and consistent
```

## Loading

With Hugging Face `datasets` (from a local clone, with the LFS audio pulled;
recent versions also need `pip install torchcodec` to decode audio):

```python
from datasets import load_dataset

ds = load_dataset("audiofolder", data_dir="data")
ds["train"][0]   # audio array + every column of metadata.csv
```

With pandas:

```python
import pandas as pd

clips = pd.read_csv("data/metadata.csv")
annotations = pd.read_csv("annotations/annotations.csv")
```

To download the audio itself (not just LFS pointer files), install
[Git LFS](https://git-lfs.com) before cloning, or run `git lfs pull` afterwards.

## `data/metadata.csv`

| Column | Description |
|---|---|
| `file_name` | Path to the audio, relative to `data/` |
| `id` | Clip ID, `<region>-NNN` |
| `old_id` | ID used before the restructure (`casablanca-1`, …) |
| `region` | `casablanca`, `oujda` or `tangier` |
| `original_filename` | Name of the source file in the original Airtable base |
| `split` | Currently `train` for every clip |
| `transcription_annotator_1` … `_3` | Each annotator's transcription, unedited |
| `majority_speaker_accent` | Label chosen by at least 2 of 3 annotators |
| `majority_register` | 〃 |
| `majority_loan_word_languages` | 〃 (`none` = no loan words) |
| `majority_genders_present` | 〃 |
| `majority_speaker_count` | 〃 |

A majority column is `no_majority` when all three annotators gave different
labels. For multi-valued labels (accent, loan-word languages, genders), order
is ignored when comparing, so `Male,Female` and `Female,Male` count as the
same answer.

## `annotations/annotations.csv`

One row per clip and annotator (`annotator_1`, `annotator_2`, `annotator_3`),
exactly as entered in Airtable:

| Column | Values |
|---|---|
| `id` | Clip ID, matches `metadata.csv` |
| `annotator_id` | `annotator_1` … `annotator_3` |
| `original_filename` | Source file name |
| `transcription` | Transcription in Arabic script; French/English words kept in Latin script |
| `speaker_accent` | `Of Casablanca`, `Of Oujda`, `Of Tangier/Tetouan`, `Other` (may list several) |
| `register` | `Moroccan Arabic`, `Mixed/Educated Moroccan Arabic`, `Standard Arabic` |
| `loan_word_languages` | e.g. `French`, `English`, `Spanish`; empty if none |
| `genders_present` | `Male`, `Female`, or both |
| `speaker_count` | `1`, `2`, `3`, `3+` |
| `audio_origin` | Region the annotator's Airtable table belonged to |

Annotators often disagree on the labels, so keep all three when a single
consensus value isn't enough.

## Sources

> _TODO: describe how the audio was collected._ Judging by the original file
> names, it includes segments of longer recorded sessions, clips from YouTube
> videos and radio recordings.

## Notes

- **Tangier includes Tetouan.** 20 Tangier clips (`tangier-019` to
  `tangier-038`) come from recordings originally named `Tetouan_…`. Their
  new IDs follow the Tangier numbering; `original_filename` keeps the source
  name so each clip can be traced back.
- **`tangier-039` is intentionally missing.** The clip
  `WwUF8uoO00c_segment_02` was filed under both Tangier and Casablanca in
  Airtable. It is kept once, as `casablanca-036`, and the Tangier number was
  left unused so that `id` and `old_id` stay aligned.
- **Splits.** Every clip is currently `train`. If you add validation/test
  splits, keep segments of the same source recording (same YouTube ID or same
  session prefix) in the same split to avoid leakage.

## License

_TODO_

## Citation

_TODO_
