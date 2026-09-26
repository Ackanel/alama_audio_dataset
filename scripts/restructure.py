"""One-off migration from the flat Airtable export to the organised layout.

Run once from the repository root, on the old layout (dataset_map.json plus one
<id>.wav and <id>.csv per clip at the top level). It:

  * moves each clip to data/audio/<region>/<region>-NNN.wav (zero-padded ID)
  * merges the per-clip CSVs into annotations/annotations.csv (one row per
    clip x annotator; transcriptions are copied exactly as written)
  * writes data/metadata.csv (one row per clip, Hugging Face "audiofolder"
    format) with the three transcriptions and majority-vote labels
  * resolves the WwUF8uoO00c_segment_02 clip, which the export filed under both
    Tangier and Casablanca, as Casablanca only
  * deletes the old per-clip CSVs and dataset_map.json

Kept in the repository as a record of how the new layout was produced.
"""

import csv
import json
import os
import shutil
from collections import Counter

DUPLICATE_CLIP = "WwUF8uoO00c_segment_02.mp3_16k.wav"
DUPLICATE_KEEP_REGION = "casablanca"

# Old CSV header -> new column name
COLUMNS = {
    "Name": "original_filename",
    "Transcription": "transcription",
    "Speaker Accent": "speaker_accent",
    "Register": "register",
    "Loan Word Languages": "loan_word_languages",
    "Genders Present": "genders_present",
    "Speaker Count": "speaker_count",
    "Audio Origin": "audio_origin",
    "annotator_id": "annotator_id",
}
LABELS = ["speaker_accent", "register", "loan_word_languages",
          "genders_present", "speaker_count"]
MULTI_VALUED = {"speaker_accent", "loan_word_languages", "genders_present"}
ANNOTATORS = ["annotator_1", "annotator_2", "annotator_3"]


def normalise(field, value):
    """Canonical form used only for comparing labels ("Male,Female" == "Female,Male")."""
    value = value.strip()
    if field in MULTI_VALUED:
        parts = sorted(p.strip() for p in value.split(",") if p.strip())
        value = ",".join(parts)
    if field == "loan_word_languages" and not value:
        value = "none"
    return value


def majority(field, values):
    """Label chosen by at least 2 of the 3 annotators, else 'no_majority'."""
    counts = Counter(normalise(field, v) for v in values)
    value, n = counts.most_common(1)[0]
    return value if n >= 2 else "no_majority"


def main():
    with open("dataset_map.json", encoding="utf-8") as f:
        entries = json.load(f)

    metadata_rows, annotation_rows = [], []

    for e in entries:
        region = e["audio_origin"].lower()
        old_id = e["id"]
        if e["original_filename"] == DUPLICATE_CLIP and region != DUPLICATE_KEEP_REGION:
            print(f"skipping {old_id}: duplicate of the {DUPLICATE_KEEP_REGION} copy")
            continue

        number = int(old_id.rsplit("-", 1)[1])
        new_id = f"{region}-{number:03d}"
        audio_rel = f"audio/{region}/{new_id}.wav"

        with open(e["transcription_file"], encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        if e["original_filename"] == DUPLICATE_CLIP:
            # The export merged both copies' annotations into this file.
            rows = [r for r in rows if r["Audio Origin"].lower() == region]

        rows = [{COLUMNS[k]: v for k, v in r.items()} for r in rows]
        by_annotator = {r["annotator_id"]: r for r in rows}
        assert sorted(by_annotator) == ANNOTATORS and len(rows) == 3, old_id

        for r in rows:
            annotation_rows.append({"id": new_id, **r})

        meta = {
            "file_name": audio_rel,
            "id": new_id,
            "old_id": old_id,
            "region": region,
            "original_filename": e["original_filename"],
            "split": e["data_split"],
        }
        for a in ANNOTATORS:
            meta[f"transcription_{a}"] = by_annotator[a]["transcription"]
        for field in LABELS:
            meta[f"majority_{field}"] = majority(field, [r[field] for r in rows])
        metadata_rows.append(meta)

        os.makedirs(f"data/audio/{region}", exist_ok=True)
        shutil.move(e["audio_file"], f"data/{audio_rel}")

    metadata_rows.sort(key=lambda r: r["id"])
    annotation_rows.sort(key=lambda r: (r["id"], r["annotator_id"]))

    with open("data/metadata.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(metadata_rows[0]))
        w.writeheader()
        w.writerows(metadata_rows)

    os.makedirs("annotations", exist_ok=True)
    with open("annotations/annotations.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id"] + list(COLUMNS.values()))
        w.writeheader()
        w.writerows(annotation_rows)

    for e in entries:
        for key in ("transcription_file", "audio_file"):
            if os.path.exists(e[key]):
                os.remove(e[key])
    os.remove("dataset_map.json")

    print(f"{len(metadata_rows)} clips, {len(annotation_rows)} annotation rows")


if __name__ == "__main__":
    main()
