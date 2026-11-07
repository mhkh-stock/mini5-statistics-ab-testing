# Mini #5 — Statistics & A/B Testing Pack

**Repo:** https://github.com/mhkh-stock/mini5-statistics-ab-testing

**SAMPLE / DEMO data only.** Fictional shop, fictional experiment,
fictional visitors. Never claimed as real client or real business data.

The statistics recruiters and clients actually expect behind an
"A/B test won" claim: conversion rates, uplift, a two-proportion
z-test, a 95% confidence interval, and the SRM check that catches a
broken test before anyone celebrates it. Every number below is
computed by the pack itself — nothing is hand-typed — and
`run_analysis.py` re-proves all of it on every run.

## The experiment story

A fictional online shop tests a new checkout button (B) against the
current button (A). 14 days, 1–14 Oct 2026, 50/50 allocation, the
same number of visitors per variant every day (210–350 a day):
4,000 visitors per variant over the 14 days, 8,000 total. Data: `data/raw/experiment_SAMPLE.csv` · Schema:
`data/schema.sql` · Seed: `data/seed.sql` (generation method
documented in `data/README.md`) · Built database: `data/demo.db`
(rebuilt any time with `python3 run_analysis.py`, which also verifies
everything; the `.db` is a runner artifact, not a deliverable).

## How to run (3 steps)

1. `cd mini5-statistics-ab-testing`
2. `python3 run_analysis.py` — builds `data/demo.db`, runs all 4 SQL
   queries, runs the statistics, writes `outputs/*.txt`, and asserts
   the 12 checks below
3. Run the statistics by hand, e.g.
   `python3 analysis/ab_test.py` (reads `data/demo.db`, writes
   `outputs/ab_results.txt`), or any query by hand, e.g.
   `sqlite3 -header -column data/demo.db < sql/01_overall_rates.sql`

Requires Python 3 + SQLite (standard library only — the normal CDF
comes from `math.erf`, no scipy). Verified on SQLite 3.45.1.

## Files

| File | What it does | Teaches |
|---|---|---|
| `sql/01_overall_rates.sql` | Conversion rate per variant | GROUP BY aggregation to test totals |
| `sql/02_daily_rates.sql` | Daily rate per variant (28 rows) | Single days are noisy: A wins 3 of 14 days, ties one |
| `sql/03_variant_by_day.sql` | Cumulative rate per variant, day by day | The anti-peeking view: the gap wobbles as days accumulate |
| `sql/04_segment_summary.sql` | Rate per variant per device | Segment check: B wins on both devices, not a mix artifact |
| `analysis/ab_test.py` | z-test, 95% CI, SRM chi-square, verdict | The full statistics, stdlib only |
| `run_analysis.py` | Builds DB, runs queries + statistics, asserts 12 checks | Verification as code, not as a promise |

## How to read the verdict

- **Rates first:** B converts at 14.400% vs A's 11.675%.
- **Uplift:** +2.725 percentage points, +23.3% relative — and
  +109 conversions over the test itself.
- **Significance:** z = 3.619, two-sided p = 0.00030 — a gap this
  big would be rare if the buttons were truly equal. That is NOT a
  99.97% chance B is better; p is about the data under "no
  difference", not about B.
- **Confidence interval:** 1.250 to 4.200 percentage points. It
  excludes zero, agreeing with p < 0.05 — and its low end (1.25pp)
  is the honest planning number, not the headline 2.73pp.
- **SRM check:** visitors split exactly 4,000/4,000, chi-square =
  0.000, p = 1.000 — clean. A skewed split would void the test no
  matter how good the p-value looked.
- **Verdict: SHIP B** — with the guardrails below.

## Guardrails this pack teaches

1. **SRM first.** Sample ratio mismatch means the allocation itself
   broke (bad randomisation, a logging bug, a bot flood). Check the
   split before reading the p-value; a significant result on a
   skewed split is not a result.
2. **Don't peek.** Daily rates flip (A wins 2 Oct, 5 Oct, 8 Oct)
   and the cumulative gap wobbles. Stopping the day your variant
   first looks ahead, or re-checking until p dips below 0.05,
   manufactures false wins. Decide the runtime in advance, read the
   verdict once, at the end.
3. **Significant is not automatically a business win.** The test
   says B converts better; it says nothing about implementation
   cost, support load, or whether +109 conversions over 14 days
   pays for the change. The absolute gain — not the relative
   percentage — is what a business case is built on.

## Verified numbers (computed by the pack, not hand-typed)

| Metric | Value |
|---|---|
| A (current button) | 4,000 visitors · 467 conversions · 11.675% |
| B (new button) | 4,000 visitors · 576 conversions · 14.400% |
| Uplift | +2.725 percentage points · +23.3% relative · +109 conversions |
| z-statistic | 3.619 |
| p-value (two-sided) | 0.00030 |
| 95% CI for the difference | 1.250 to 4.200 percentage points |
| SRM check | chi-square 0.000 · p = 1.000 · split 4,000/4,000 — clean |
| Device split | A: mobile 280/2,400 (11.67%), desktop 187/1,600 (11.69%) · B: mobile 346/2,400 (14.42%), desktop 230/1,600 (14.38%) — B wins on both |
| Checks | 12/12 pass on every run |

## Verification (done before delivery)

- All 4 queries execute against `data/demo.db` with no errors
  (2, 28, 28, and 4 rows respectively).
- `run_analysis.py` asserts 12 checks as code: CSV totals = SQL
  totals = analysis inputs; rates recompute; z, p, and the CI
  recompute independently of the analysis module; p < 0.05; the
  CI excludes 0; the SRM check is clean and recomputes; device
  totals reconcile to overall totals; all 5 output files exist,
  non-empty, with the expected row counts.
- Verified outputs are saved in `outputs/` (one `.txt` per query
  plus `ab_results.txt`); the runner re-asserts all of the above
  on every run.

## Limits

- **SAMPLE data only.** The experiment is fictional; the numbers
  show the method, not a real business result. Do not cite them as
  evidence about any real shop or button.
- **No a priori power or sample-size calculation.** The test ran a
  fixed 14 days with the traffic it got (4,000 per variant); the
  pack verifies the result, it does not size the test in advance.
- **One test, one verdict.** No multiple-comparison correction is
  applied — running several variants or re-testing until p < 0.05
  would need one, and would void the p-value above.
- **The device split is a segment check, not a second test.** B
  wins on both devices, which rules out a mix artifact; it is not
  a separately powered claim about mobile or desktop alone.
- **Fixed horizon.** The verdict is read once, at day 14. The
  cumulative view (query 03) is there to show why peeking mid-test
  would have been a guess, not to support an earlier call.

## Published

Live on GitHub: https://github.com/mhkh-stock/mini5-statistics-ab-testing
(published 4 Nov 2026, 16 files live). The built `data/demo.db` is
intentionally not uploaded — rebuild it any time with
`python3 run_analysis.py`.
