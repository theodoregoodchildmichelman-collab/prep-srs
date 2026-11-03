# prep-srs

Theo's prep-lesson review deck (LSAT · GRE · FSOT course), in the "Foreign Service + LSAT PREP" project. It holds the content cards (C###) and the vocabulary cards (V###). Only `srs.py` changes `cards.json`: lessons read the cards that are due and record results, and nobody rewrites the whole deck.

## In a lesson
```bash
git clone --depth 1 https://github.com/theodoregoodchildmichelman-collab/prep-srs /home/claude/prep-srs   # or git pull
cd /home/claude/prep-srs
python3 srs.py due                      # today's recall slot: up to 8 C cards + up to 3 V cards
python3 srs.py grade C032 half unsure --lesson 19 --note "pacing given as 2:00 only"
python3 srs.py grade V019 ok sure --format "define + contrast" --lesson 19
python3 srs.py add --track E --q "..." --a "..." --lesson 19
python3 srs.py add-v --word onerous --meaning "..." --use "..." --confusable "..." --example "..." --lesson 19
python3 srs.py stats                    # counts for the lesson-log header
git add -A && git commit -m "Lesson #19: grades + new cards" && git push
```
Other commands: `backlog` (every due card, one line each, for Friday review), `show C032` (full card and history), `note C032 "text"`, `edit C032 --q "..."`.

## Rules
- **Results:** `ok`, `half` or `miss`. **Confidence:** `sure` or `unsure` (or 1–3, or `-` if not given).
- Correct → up one box. Half or wrong → Box 1. Correct but unsure (or confidence 1) → stays in its box.
- A wrong answer given as sure is a confident miss: ⚠️, kept in Box 1 until answered correctly twice. ⚠️ cards come first in `due`.
- Intervals: Box 1 = the next lesson day (the next weekday) · Box 2 = +3 days · Box 3 = +7 · Box 4 = +16 · Box 5 = +35. A due date on a weekend rolls to Monday. Correct in Box 5 → retired.
- Recall slot: at most 8 C cards, oldest due first (Box 1 first when more than 10 are due), mixing at least 2 tracks; at most 3 V cards, Box 1 first, with a suggested format rotating cloze → produce → discriminate → define + contrast.
- Tracks: L logic · E econ/systems · P ideas · Q quant · H US govt/history · W world history/affairs · G English usage · T test strategy · GQ GRE quant · GV GRE verbal · WR writing · V vocabulary. Timed-LR (TL) misses become L cards.

## Files
- `cards.json`: the deck. Each card has its box, due date, a `history` (notes carried over from the markdown deck) and a `log` (one entry per graded test).
- `srs.py`: the only thing that edits the deck.
- `archive/`: the last markdown versions of the deck (2026-11-02), kept verbatim, plus older lesson-log and learner-profile notes moved out of the project docs.
- `tools/migrate_2026_11.py`: the one-time conversion from markdown.

The rest of the course (curriculum, lesson log, word bank and queue, application timeline) stays in the claude.ai project docs.
