# ALAMA Audio Dataset

Short audio clips of Moroccan Arabic (Darija) speech from three cities (Casablanca, Tangier, Oujda) each transcribed and labelled
independently by three annotators.

Audio is 16 kHz WAV, about 115 MB in total, stored with Git LFS.

We made this dataset to explicitly identify Moroccan Arabic on the sub-dialect level. Moroccan Arabic can change
dramatically depending on the region, yet most datasets for Moroccan Arabic don't label local provenance. This small, pilot dataset hopes to be useful for researchers looking into intra-dialect differences for Moroccan Arabic.

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

This dataset was gathered from local radio audio data around Morocco, we also made use of suitable audio from the ARCADE dataset. Around nine minutes of our audio for the Casablanca subsection and three minutes for the Tangier subsection come from ARCADE. [`riotu-lab/ARCADE-full`](https://huggingface.co/datasets/riotu-lab/ARCADE-full)
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 

If you use this dataset, please also cite ARCADE:

```bibtex
@misc{nacar2026arcadecityscalecorpusfinegrained,
      title={ARCADE: A City-Scale Corpus for Fine-Grained Arabic Dialect Tagging},
      author={Omer Nacar and Serry Sibaee and Adel Ammar and Yasser Alhabashi and Nadia Samer Sibai and Yara Farouk Ahmed and Ahmed Saud Alqusaiyer and Sulieman Mahmoud AlMahmoud and Abdulrhman Mamdoh Mukhaniq and Lubaba Raed and Sulaiman Mohammed Alatwah and Waad Nasser Alqahtani and Yousif Abdulmajeed Alnasser and Mohamed Aziz Khadraoui and Wadii Boulila},
      year={2026},
      eprint={2601.02209},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2601.02209},
}
```

## Citation

@misc{alama_audio_dataset_2026,
  title        = {{ALAMA} Audio Dataset: Transcribed Moroccan Arabic Speech from Casablanca, Oujda and Tangier>},
  author       = {Avery Cole Kanel and Christian Schuler and Bouazza Laracha and Imrane Lbouhli and Yassine Chaouri and Yusser Al Ghussin and Timo Baumann},
  year         = {2026},
  howpublished = {GitHub repository},
  url          = {https://github.com/Ackanel/alama_audio_dataset}
}
