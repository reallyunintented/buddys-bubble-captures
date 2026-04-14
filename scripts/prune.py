#!/usr/bin/env python3
"""Remove bubbles from bubbles.jsonl by index (0-based) or by substring match.

Usage:
    scripts/prune.py 4 17 88              # remove bubbles at those indices
    scripts/prune.py --grep "test run"    # remove any bubble whose text contains this
    scripts/prune.py --list               # show all bubbles with their indices
    scripts/prune.py --dry-run 4 17       # preview which would be removed without writing
"""
import json
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "bubbles.jsonl"


def load():
    with PATH.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def save(bubbles, backup=True):
    if backup:
        shutil.copy(PATH, PATH.with_suffix(".jsonl.bak"))
    with PATH.open("w") as f:
        for b in bubbles:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")


def list_all():
    for i, b in enumerate(load()):
        preview = b["text"].replace("\n", " ")[:110]
        print(f"{i:4d}  {b['timestamp'][:19]}  {preview}")


def prune_by_indices(idxs, dry=False):
    bubbles = load()
    idxs = set(int(i) for i in idxs)
    invalid = [i for i in idxs if i < 0 or i >= len(bubbles)]
    if invalid:
        print(f"ERROR: out-of-range indices: {invalid} (valid: 0..{len(bubbles)-1})")
        sys.exit(1)
    kept, removed = [], []
    for i, b in enumerate(bubbles):
        (removed if i in idxs else kept).append((i, b))
    print(f"{'Would remove' if dry else 'Removing'} {len(removed)} bubble(s):")
    for i, b in removed:
        print(f"  [{i}] {b['text'][:100]}")
    if not dry:
        save([b for _, b in kept])
        print(f"Saved. {len(bubbles)} → {len(kept)} bubbles. Backup: bubbles.jsonl.bak")


def prune_by_grep(needle, dry=False):
    bubbles = load()
    needle_l = needle.lower()
    kept, removed = [], []
    for i, b in enumerate(bubbles):
        (removed if needle_l in b["text"].lower() else kept).append((i, b))
    if not removed:
        print(f"No bubbles match: {needle!r}")
        return
    print(f"{'Would remove' if dry else 'Removing'} {len(removed)} bubble(s) matching {needle!r}:")
    for i, b in removed:
        print(f"  [{i}] {b['text'][:100]}")
    if not dry:
        save([b for _, b in kept])
        print(f"Saved. {len(bubbles)} → {len(kept)} bubbles. Backup: bubbles.jsonl.bak")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if args[0] == "--list":
        list_all()
        return
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    if args and args[0] == "--grep":
        if len(args) < 2:
            print("ERROR: --grep needs a substring")
            sys.exit(1)
        prune_by_grep(args[1], dry)
    else:
        try:
            idxs = [int(a) for a in args]
        except ValueError:
            print(f"ERROR: expected integer indices, got: {args}")
            sys.exit(1)
        prune_by_indices(idxs, dry)


if __name__ == "__main__":
    main()
