# Mini #5 data

Fictional experiment, SAMPLE data only — never real client or real
business data. A fictional online shop tests a new checkout button
(B) against the current button (A), 1–14 Oct 2026, 50/50 allocation,
4,000 visitors per variant.

Generation (deterministic, reproducible): Python
`random.Random(7)`, one binomial draw per variant per day
(control p = 0.12, variant p = 0.145). Daily visitors are fixed per
day and identical for both variants, so the split is exactly
balanced. The device table allocates each variant's totals 60/40 by
visitors (mobile/desktop) and splits conversions in the same
proportion, so device totals reconcile exactly to daily totals.

Files: raw CSV `raw/experiment_SAMPLE.csv` (28 rows: 14 days × 2
variants) · Schema `schema.sql` · Seed `seed.sql` · Rebuild any time
with `python3 run_analysis.py` (also runs the statistics and checks).

## Data dictionary

`experiment_daily` — one row per day per variant (the experiment):

| Column | Type | Meaning |
|---|---|---|
| `date` | TEXT | Day of the test, `YYYY-MM-DD`, 2026-10-01 to 2026-10-14 |
| `variant` | TEXT | `A` (current button) or `B` (new button) |
| `visitors` | INTEGER | Visitors shown that variant that day (210–350; identical for A and B each day) |
| `conversions` | INTEGER | Of those visitors, how many converted |

`experiment_device` — the same totals split by device (a segment
summary, not a second experiment):

| Column | Type | Meaning |
|---|---|---|
| `variant` | TEXT | `A` or `B` |
| `device` | TEXT | `mobile` (60% of visitors) or `desktop` (40%) |
| `visitors` | INTEGER | Visitors on that device for that variant |
| `conversions` | INTEGER | Conversions on that device for that variant |

Device totals reconcile exactly to the daily totals (A: 2,400 + 1,600
= 4,000 visitors, 280 + 187 = 467 conversions; B: 2,400 + 1,600 =
4,000 visitors, 346 + 230 = 576 conversions) — asserted as a check
by `run_analysis.py`.
