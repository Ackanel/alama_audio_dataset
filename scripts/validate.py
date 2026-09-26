"""Check the dataset is complete and consistent. Run from the repository root:

    python scripts/validate.py

Exits with status 1 and lists the problems if anything is wrong.
"""

import csv
import os
import sys
from collections import Counter

ANNOTATORS = {"annotator_1", "annotator_2", "annotator_3"}


def main():
    problems = []

    with open("data/metadata.csv", encoding="utf-8", newline="") as f:
        clips = list(csv.DictReader(f))
    with open("annotations/annotations.csv", encoding="utf-8", newline="") as f:
        annotations = list(csv.DictReader(f))

    ids = Counter(c["id"] for c in clips)
    problems += [f"duplicate clip id {i}" for i, n in ids.items() if n > 1]
    sources = Counter(c["original_filename"] for c in clips)
    problems += [f"source file used by {n} clips: {s}" for s, n in sources.items() if n > 1]

    for c in clips:
        path = os.path.join("data", c["file_name"])
        if not os.path.isfile(path):
            problems.append(f"{c['id']}: missing audio {path}")
        expected = f"audio/{c['region']}/{c['id']}.wav"
        if c["file_name"] != expected:
            problems.append(f"{c['id']}: file_name should be {expected}")

    by_clip = {}
    for a in annotations:
        by_clip.setdefault(a["id"], []).append(a)
        if a["id"] not in ids:
            problems.append(f"annotation for unknown clip {a['id']}")

    for c in clips:
        rows = by_clip.get(c["id"], [])
        found = {r["annotator_id"] for r in rows}
        if len(rows) != 3 or found != ANNOTATORS:
            problems.append(f"{c['id']}: expected one row per annotator, found {sorted(r['annotator_id'] for r in rows)}")
        for r in rows:
            if r["original_filename"] != c["original_filename"]:
                problems.append(f"{c['id']}/{r['annotator_id']}: original_filename mismatch")
            if not r["transcription"].strip():
                problems.append(f"{c['id']}/{r['annotator_id']}: empty transcription")
            if c[f"transcription_{r['annotator_id']}"] != r["transcription"]:
                problems.append(f"{c['id']}/{r['annotator_id']}: transcription differs from metadata.csv")

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    regions = Counter(c["region"] for c in clips)
    print(f"OK: {len(clips)} clips ({', '.join(f'{r} {n}' for r, n in sorted(regions.items()))}), "
          f"{len(annotations)} annotations")


if __name__ == "__main__":
    main()
