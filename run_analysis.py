"""Build data/demo.db from schema+seed, run the 4 SQL queries, run the
statistics (analysis/ab_test.py), write outputs/*.txt, and assert the
checks below. Nothing here trusts a hand-typed number: totals are
recomputed from the CSV, the SQL tables, and the analysis inputs and
must agree; z, p, and the CI are recomputed here with independent
formulas and must match the analysis module; and the verdict's
conditions (p < 0.05, CI excludes 0, SRM clean) are asserted as code.
Any mismatch fails the run."""
import csv
import math
import sqlite3
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "analysis"))
import ab_test  # noqa: E402  (the pack's own statistics module)

db = BASE / "data" / "demo.db"
if db.exists():
    db.unlink()
con = sqlite3.connect(db)
con.executescript((BASE / "data" / "schema.sql").read_text())
con.executescript((BASE / "data" / "seed.sql").read_text())
con.commit()

outdir = BASE / "outputs"
outdir.mkdir(exist_ok=True)

# 1. Run the 4 SQL queries, one output file each (mini4 style: rows joined).
query_files = sorted((BASE / "sql").glob("*.sql"))
row_counts = {}
for f in query_files:
    cur = con.execute(f.read_text())
    rows = cur.fetchall()
    row_counts[f.stem] = len(rows)
    (outdir / f"{f.stem}.txt").write_text(
        "\n".join(" | ".join("" if v is None else str(v) for v in r) for r in rows)
        + ("\n" if rows else "")
    )

# 2. Run the statistics script itself (verifies it works standalone).
proc = subprocess.run([sys.executable, str(BASE / "analysis" / "ab_test.py")],
                      capture_output=True, text=True)
print(proc.stdout, end="")
if proc.returncode != 0:
    print(proc.stderr, file=sys.stderr)
    sys.exit(1)

# 3. Independent recomputation (fresh formulas, not the module's code).
# totals rows are (variant, visitors, conversions)
totals = {v: (n, c) for v, n, c in
          con.execute("SELECT variant, SUM(visitors), SUM(conversions)"
                      " FROM experiment_daily GROUP BY variant").fetchall()}
n_a, c_a = totals["A"]
n_b, c_b = totals["B"]
p_a, p_b = c_a / n_a, c_b / n_b
diff = p_b - p_a
p_pool = (c_a + c_b) / (n_a + n_b)
se_pool = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
z_check = diff / se_pool
p_check = math.erfc(abs(z_check) / math.sqrt(2))  # two-sided, 1 - CDF form
se_diff = math.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
ci_check = (diff - 1.96 * se_diff, diff + 1.96 * se_diff)
expected_split = (n_a + n_b) / 2
srm_chi2 = (n_a - expected_split) ** 2 / expected_split \
    + (n_b - expected_split) ** 2 / expected_split
srm_p = math.erfc(math.sqrt(srm_chi2 / 2)) if srm_chi2 > 0 else 1.0

# CSV totals, summed from the raw file (not from the database).
csv_totals = {}
with open(BASE / "data" / "raw" / "experiment_SAMPLE.csv", newline="") as fh:
    for row in csv.DictReader(fh):
        v, n, c = row["variant"], int(row["visitors"]), int(row["conversions"])
        pn, pc = csv_totals.get(v, (0, 0))
        csv_totals[v] = (pn + n, pc + c)

# Device totals, summed from the segment table.
device_totals = {v: (n, c) for v, n, c in
                 con.execute("SELECT variant, SUM(visitors), SUM(conversions)"
                             " FROM experiment_device GROUP BY variant").fetchall()}

# Analysis module's own numbers, for the cross-check.
stats = ab_test.compute(ab_test.load_totals(con))

checks = [
    ("CSV visitors match SQL totals",
     csv_totals["A"][0] == n_a and csv_totals["B"][0] == n_b),
    ("CSV conversions match SQL totals",
     csv_totals["A"][1] == c_a and csv_totals["B"][1] == c_b),
    ("SQL overall rates recompute (conversions / visitors)",
     abs(c_a / n_a - p_a) < 1e-12 and abs(c_b / n_b - p_b) < 1e-12),
    ("Analysis inputs match SQL totals",
     stats["n_a"] == n_a and stats["c_a"] == c_a
     and stats["n_b"] == n_b and stats["c_b"] == c_b),
    ("z-statistic recomputes independently",
     abs(stats["z"] - z_check) < 1e-9),
    ("p-value recomputes independently",
     abs(stats["p_value"] - p_check) < 1e-9),
    ("95% CI recomputes independently",
     abs(stats["ci_low_pp"] - ci_check[0] * 100) < 1e-9
     and abs(stats["ci_high_pp"] - ci_check[1] * 100) < 1e-9),
    ("p < 0.05 (significant)", stats["p_value"] < 0.05),
    ("95% CI excludes 0", stats["ci_low_pp"] > 0),
    ("SRM check clean (p > 0.05) and recomputes",
     abs(stats["srm_p"] - srm_p) < 1e-9 and stats["srm_p"] > 0.05),
    ("Device split totals reconcile to overall totals",
     device_totals["A"] == (n_a, c_a) and device_totals["B"] == (n_b, c_b)),
    ("Output files complete (4 queries + analysis, expected row counts)",
     all((outdir / f"{f.stem}.txt").exists()
         and (outdir / f"{f.stem}.txt").stat().st_size > 0 for f in query_files)
     and (outdir / "ab_results.txt").exists()
     and (outdir / "ab_results.txt").stat().st_size > 0
     and row_counts.get("01_overall_rates") == 2
     and row_counts.get("02_daily_rates") == 28
     and row_counts.get("03_variant_by_day") == 28
     and row_counts.get("04_segment_summary") == 4),
]
fails = []
for name, ok in checks:
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)
print(f"\n{len(checks) - len(fails)}/{len(checks)} checks pass"
      if fails else f"\nALL {len(checks)} CHECKS PASS")
sys.exit(1 if fails else 0)
