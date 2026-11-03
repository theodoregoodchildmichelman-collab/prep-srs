#!/usr/bin/env python3
"""prep-srs: Theo's prep-lesson review deck (content cards C### and vocab cards V###).

The deck lives in cards.json. Lessons read only the cards that are due and record
results with `grade`; the script applies the Leitner rules and the dates, so nobody
reads or rewrites the whole deck by hand.

Commands (run from the repo root):
  python3 srs.py due [--date D] [--max 8] [--vmax 3]   cards for today's recall slot
  python3 srs.py backlog [--date D]                    every due card, one line each
  python3 srs.py show C032 V019 ...                    full card(s), with history
  python3 srs.py grade C032 half unsure [--note "..."] [--lesson 19] [--format cloze]
        result: ok | half | miss      confidence: sure | unsure | 1-3 | -   (- = not given)
  python3 srs.py add --track L --q "..." --a "..." [--note "..."] [--lesson 19]
  python3 srs.py add-v --word onerous --meaning "..." --use "..." --confusable "..." --example "..." [--lesson 19]
  python3 srs.py note C032 "text"                      append a coaching note
  python3 srs.py edit C032 --q "..." | --a "..."       replace a field
  python3 srs.py stats                                 header counts for the lesson log

Rules (same as the course has used since Oct 2026):
  Boxes 1-5. Correct -> up one box. Half or wrong -> Box 1. Correct but unsure (or conf <= 1)
  -> stays in its box. A wrong answer given as sure (conf >= 2.5) is a confident miss: flagged
  ⚠️ and kept in Box 1 until answered correctly twice. Correct in Box 5 -> retired.
  Intervals: Box 1 = next lesson day (next weekday), Box 2 = +3 days, Box 3 = +7, Box 4 = +16,
  Box 5 = +35; a due date on a weekend rolls to Monday.
  Recall slot: at most 8 C cards (oldest due first; Box 1 first when more than 10 are due;
  at least 2 tracks) and at most 3 V cards (Box 1 first).
"""
import argparse
import datetime as dt
import json
import os
import sys

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Skopje")
except Exception:  # pragma: no cover
    TZ = None

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(HERE, "cards.json")
INTERVAL = {2: 3, 3: 7, 4: 16, 5: 35}
V_FORMATS = ["cloze", "produce", "discriminate", "define + contrast"]


def today():
    now = dt.datetime.now(TZ) if TZ else dt.datetime.now()
    return now.date()


def parse_date(s):
    return dt.date.fromisoformat(s) if s else today()


def roll_weekend(d):
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def next_lesson_day(d):
    return roll_weekend(d + dt.timedelta(days=1))


def due_date(box, d):
    if box <= 1:
        return next_lesson_day(d)
    return roll_weekend(d + dt.timedelta(days=INTERVAL[box]))


def load():
    with open(DECK, encoding="utf-8") as f:
        return json.load(f)


def save(deck, d):
    deck["meta"]["updated"] = d.isoformat()
    tmp = DECK + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, DECK)


def find(deck, cid):
    cid = cid.upper()
    for c in deck["cards"]:
        if c["id"] == cid:
            return c
    sys.exit(f"No card {cid}")


def is_v(c):
    return c["id"].startswith("V")


def conf_kind(conf):
    """Return 'sure', 'unsure' or None (not given / middling)."""
    if conf is None or conf in ("-", ""):
        return None
    c = str(conf).lower()
    if c in ("sure", "s", "yes"):
        return "sure"
    if c in ("unsure", "u", "no", "guess"):
        return "unsure"
    try:
        x = float(c)
    except ValueError:
        sys.exit(f"Confidence must be sure, unsure, 1-3 or -, not {conf!r}")
    if x >= 2.5:
        return "sure"
    if x <= 1:
        return "unsure"
    return None


def last_result(c):
    if c.get("log"):
        e = c["log"][-1]
        return f'{e["result"]} {e["date"][5:]}'
    return "—"


def tail(text, n=260):
    text = (text or "").strip()
    if len(text) <= n:
        return text
    cut = text[-n:]
    sp = cut.find(" ")
    return "…" + cut[sp + 1:] if sp != -1 else "…" + cut


def flag(c):
    return " ⚠️" if c.get("warn", 0) > 0 else ""


def head(c):
    return f'{c["id"]} · {c["track"]} · Box {c["box"]}{flag(c)} · due {c["next_due"]} · last {last_result(c)}'


def next_v_format(c):
    used = [e.get("format") for e in c.get("log", []) if e.get("format")]
    if not used:
        return V_FORMATS[0]
    last = used[-1]
    i = V_FORMATS.index(last) if last in V_FORMATS else -1
    return V_FORMATS[(i + 1) % len(V_FORMATS)]


def print_card(c, full=False):
    print(head(c))
    if is_v(c):
        print(f'  Word: {c["word"]}')
        print(f'  Meaning: {c["meaning"]}')
        if c.get("use"):
            print(f'  Use: {c["use"]}')
        if c.get("confusable"):
            print(f'  Confusable: {c["confusable"]}')
        if c.get("example"):
            print(f'  Example: {c["example"]}')
        if not full:
            print(f'  Suggested format: {next_v_format(c)}')
    else:
        print(f'  Q: {c["q"]}')
        print(f'  A: {c["a"]}')
    notes = c.get("history", "")
    if full:
        print(f'  Created: {c.get("created", "")}')
        if notes:
            print(f"  History: {notes}")
        for e in c.get("log", []):
            bits = [e["date"], f'#{e["lesson"]}' if e.get("lesson") else "", e["result"],
                    e.get("conf") or "", e.get("format") or "", e.get("note") or ""]
            print("  · " + " ".join(b for b in bits if b))
    else:
        recent = " | ".join(e["note"] for e in c.get("log", [])[-2:] if e.get("note"))
        if recent:
            print(f"  Recent: {tail(recent, 220)}")
        elif notes:
            print(f"  Note: {tail(notes)}")
    print()


def due_cards(deck, d, v):
    return [c for c in deck["cards"]
            if c.get("status", "active") == "active" and is_v(c) == v
            and dt.date.fromisoformat(c["next_due"]) <= d]


def pick(cards, n, box1_first, mix_tracks):
    def key(c):
        b = 0 if (box1_first and c["box"] == 1) else 1
        w = 0 if c.get("warn", 0) > 0 else 1  # confident misses first
        return (w, b, c["next_due"], c["box"], c["id"])
    ordered = sorted(cards, key=key)
    chosen = ordered[:n]
    if mix_tracks and chosen and len({c["track"] for c in chosen}) < 2:
        other = next((c for c in ordered[n:] if c["track"] != chosen[0]["track"]), None)
        if other:
            chosen[-1] = other
    return chosen


def cmd_due(a):
    deck, d = load(), parse_date(a.date)
    cs, vs = due_cards(deck, d, False), due_cards(deck, d, True)
    pc = pick(cs, a.max, box1_first=len(cs) > 10, mix_tracks=True)
    pv = pick(vs, a.vmax, box1_first=True, mix_tracks=False)
    print(f"== {d.isoformat()} · {len(cs)} C cards due, showing {len(pc)} · "
          f"{len(vs)} V cards due, showing {len(pv)} ==\n")
    for c in pc:
        print_card(c)
    if pv:
        print("-- Vocab slot --\n")
    for c in pv:
        print_card(c)
    rest = [c["id"] for c in cs if c not in pc] + [c["id"] for c in vs if c not in pv]
    if rest:
        print(f"Still due after today ({len(rest)}): {' '.join(rest)}")


def cmd_backlog(a):
    deck, d = load(), parse_date(a.date)
    for v in (False, True):
        cs = sorted(due_cards(deck, d, v), key=lambda c: (c["box"], c["next_due"], c["id"]))
        print(f'{"V" if v else "C"} cards due: {len(cs)}')
        for c in cs:
            label = c["word"] if v else c["q"][:70]
            print(f'  {c["id"]} B{c["box"]}{flag(c)} {c["next_due"]}  {label}')


def cmd_show(a):
    deck = load()
    for cid in a.ids:
        print_card(find(deck, cid), full=True)


def cmd_grade(a):
    deck, d = load(), parse_date(a.date)
    c = find(deck, a.id)
    res = {"ok": "✔", "✔": "✔", "correct": "✔", "half": "½", "½": "½",
           "miss": "✘", "✘": "✘", "wrong": "✘"}.get(a.result.lower())
    if not res:
        sys.exit("Result must be ok, half or miss")
    kind = conf_kind(a.conf)
    old_box, warn = c["box"], c.get("warn", 0)
    retired = False
    if res == "✔":
        if warn > 0:
            warn -= 1
            c["box"] = 1 if warn > 0 else 2
        elif kind == "unsure":
            pass
        elif c["box"] >= 5:
            retired = True
        else:
            c["box"] += 1
    else:
        c["box"] = 1
        if res == "✘" and kind == "sure":
            warn = 2
    c["warn"] = warn
    c["last_tested"] = d.isoformat()
    entry = {"date": d.isoformat(), "result": res}
    if a.lesson:
        entry["lesson"] = a.lesson
    if a.conf not in (None, "-"):
        entry["conf"] = str(a.conf)
    if a.format:
        entry["format"] = a.format
    if a.note:
        entry["note"] = a.note
    c.setdefault("log", []).append(entry)
    if retired:
        c["status"] = "retired"
        c["next_due"] = ""
        msg = f'{c["id"]}: {res} → retired'
    else:
        c["next_due"] = due_date(c["box"], d).isoformat()
        msg = f'{c["id"]}: {res} {a.conf or "-"} · Box {old_box} → {c["box"]}{flag(c)} · due {c["next_due"]}'
    save(deck, d)
    print(msg)


def cmd_add(a, v=False):
    deck, d = load(), parse_date(a.date)
    key = "next_v" if v else "next_c"
    n = deck["meta"][key]
    cid = f'{"V" if v else "C"}{n:03d}'
    c = {"id": cid, "track": "V" if v else a.track.upper(), "box": 1, "warn": 0}
    if v:
        c.update(word=a.word, meaning=a.meaning, use=a.use or "",
                 confusable=a.confusable or "", example=a.example or "")
    else:
        c.update(q=a.q, a=a.a)
    c.update(created=d.isoformat() + (f" (Lesson #{a.lesson})" if a.lesson else ""),
             last_tested="", next_due=next_lesson_day(d).isoformat(),
             history=a.note or "", log=[], status="active")
    deck["cards"].append(c)
    deck["meta"][key] = n + 1
    save(deck, d)
    print(f'Added {cid} · due {c["next_due"]}')


def cmd_note(a):
    deck, d = load(), today()
    c = find(deck, a.id)
    c["history"] = (c.get("history", "").rstrip() + " " + f"{d.isoformat()}: {a.text}").strip()
    save(deck, d)
    print(f'Note added to {c["id"]}')


def cmd_edit(a):
    deck, d = load(), today()
    c = find(deck, a.id)
    for field in ("q", "a", "word", "meaning", "use", "confusable", "example"):
        val = getattr(a, field, None)
        if val is not None:
            c[field] = val
    save(deck, d)
    print(f'Edited {c["id"]}')


def cmd_stats(a):
    deck, d = load(), parse_date(a.date)
    for v in (False, True):
        cs = [c for c in deck["cards"] if is_v(c) == v]
        act = [c for c in cs if c.get("status", "active") == "active"]
        boxes = {b: sum(1 for c in act if c["box"] == b) for b in range(1, 6)}
        due = due_cards(deck, d, v)
        over = [c for c in due if c["next_due"] < d.isoformat()]
        warn = [c["id"] for c in act if c.get("warn", 0) > 0]
        nxt = deck["meta"]["next_v" if v else "next_c"]
        print(f'{"V" if v else "C"}: active {len(act)} · retired {len(cs) - len(act)} · '
              f'boxes {boxes} · due {len(due)} (overdue {len(over)}) · ⚠️ {warn or "none"} · '
              f'next free {"V" if v else "C"}{nxt:03d}')
    print(f'Deck updated: {deck["meta"].get("updated", "")}')


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("due"); x.add_argument("--date"); x.add_argument("--max", type=int, default=8)
    x.add_argument("--vmax", type=int, default=3); x.set_defaults(f=cmd_due)
    x = s.add_parser("backlog"); x.add_argument("--date"); x.set_defaults(f=cmd_backlog)
    x = s.add_parser("show"); x.add_argument("ids", nargs="+"); x.set_defaults(f=cmd_show)
    x = s.add_parser("grade"); x.add_argument("id"); x.add_argument("result")
    x.add_argument("conf", nargs="?"); x.add_argument("--note"); x.add_argument("--lesson", type=int)
    x.add_argument("--format"); x.add_argument("--date"); x.set_defaults(f=cmd_grade)
    x = s.add_parser("add"); x.add_argument("--track", required=True); x.add_argument("--q", required=True)
    x.add_argument("--a", required=True); x.add_argument("--note"); x.add_argument("--lesson", type=int)
    x.add_argument("--date"); x.set_defaults(f=lambda a: cmd_add(a, False))
    x = s.add_parser("add-v"); x.add_argument("--word", required=True); x.add_argument("--meaning", required=True)
    x.add_argument("--use"); x.add_argument("--confusable"); x.add_argument("--example")
    x.add_argument("--note"); x.add_argument("--lesson", type=int); x.add_argument("--date")
    x.set_defaults(f=lambda a: cmd_add(a, True))
    x = s.add_parser("note"); x.add_argument("id"); x.add_argument("text"); x.set_defaults(f=cmd_note)
    x = s.add_parser("edit"); x.add_argument("id")
    for field in ("q", "a", "word", "meaning", "use", "confusable", "example"):
        x.add_argument(f"--{field}")
    x.set_defaults(f=cmd_edit)
    x = s.add_parser("stats"); x.add_argument("--date"); x.set_defaults(f=cmd_stats)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
