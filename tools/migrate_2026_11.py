#!/usr/bin/env python3
"""One-time migration (2026-11-03): archive/03 + archive/05 markdown cards -> cards.json."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD_C = re.compile(r"^### (C\d{3}) · (\w+) · Box (\d)( ⚠️)?\s*$")
HEAD_V = re.compile(r"^### (V\d{3}) · (.+?) · Box (\d)( ⚠️)?\s*$")
DATES = re.compile(r"^Created: (.*?) · Last tested: (.*?) · Next due: (\d{4}-\d{2}-\d{2})")


def blocks(path, head):
    cur, out = None, []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = head.match(line)
            if m:
                cur = {"m": m, "lines": []}
                out.append(cur)
            elif line.startswith("## ") and cur:
                cur = None
            elif cur is not None and line.strip():
                cur["lines"].append(line)
    return out


def field(lines, prefix):
    for l in lines:
        if l.startswith(prefix):
            return l[len(prefix):].strip()
    return ""


def common(b):
    m, lines = b["m"], b["lines"]
    dm = None
    for l in lines:
        dm = DATES.match(l)
        if dm:
            break
    if not dm:
        sys.exit(f"No dates line for {m.group(1)}")
    last = dm.group(2).strip()
    return {
        "box": int(m.group(3)),
        "warn": 1 if m.group(4) else 0,  # only C042 (one correct run done, needs one more)
        "created": dm.group(1).strip(),
        "last_tested": "" if last in ("—", "-") else last,
        "next_due": dm.group(3),
        "history": field(lines, "History:"),
        "log": [],
        "status": "active",
    }


def main():
    cards = []
    for b in blocks(os.path.join(ROOT, "archive/03-review-cards-2026-11-02.md"), HEAD_C):
        c = {"id": b["m"].group(1), "track": b["m"].group(2),
             "q": field(b["lines"], "Q:"), "a": field(b["lines"], "A:")}
        c.update(common(b))
        if not c["q"] or not c["a"]:
            sys.exit(f"Missing Q/A in {c['id']}")
        cards.append(c)
    for b in blocks(os.path.join(ROOT, "archive/05-vocab-cards-2026-11-02.md"), HEAD_V):
        meaning_line = field(b["lines"], "Meaning:")
        parts = re.split(r" · (?:Use note|Confusable with): ", meaning_line)
        if len(parts) != 3:
            sys.exit(f"Unexpected Meaning line in {b['m'].group(1)}")
        c = {"id": b["m"].group(1), "track": "V", "word": b["m"].group(2),
             "meaning": parts[0], "use": parts[1], "confusable": parts[2],
             "example": field(b["lines"], "Example (from lesson):")}
        c.update(common(b))
        cards.append(c)
    deck = {"meta": {"next_c": 60, "next_v": 24, "updated": "2026-11-03",
                     "migrated_from": "claude/03-review-cards.md + V cards of claude/05-vocab.md (2026-11-02)"},
            "cards": cards}
    with open(os.path.join(ROOT, "cards.json"), "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{sum(1 for c in cards if c['id'][0] == 'C')} C cards, "
          f"{sum(1 for c in cards if c['id'][0] == 'V')} V cards")


if __name__ == "__main__":
    main()
