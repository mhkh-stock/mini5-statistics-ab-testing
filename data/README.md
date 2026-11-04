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
