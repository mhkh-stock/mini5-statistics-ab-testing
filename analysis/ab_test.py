"""Mini #5 statistics: two-proportion z-test, 95% confidence interval,
and SRM (sample ratio mismatch) chi-square check for a two-variant
A/B test. Standard library only (math.erf supplies the normal CDF) so
the pack runs anywhere — no scipy needed.

Reads data/demo.db (built by run_analysis.py from data/schema.sql +
data/seed.sql), writes outputs/ab_results.txt, and prints it.

What each number means, in one line each:
- conversion rate: conversions / visitors, per variant.
- uplift: variant rate minus control rate (percentage points), and
  that difference as a percentage of the control rate (relative %).
- z-statistic / p-value: two-proportion z-test with a pooled standard
  error. p < 0.05 means a gap this big would be rare if the variants
  were truly equal — it is not a 95% chance B is better.
- 95% CI for the difference: the range of true differences compatible
  with the data. It must exclude 0 to agree with p < 0.05.
- SRM check: with a 50/50 allocation the visitor split should be
  ~50/50. A chi-square p <= 0.05 means the split itself is skewed
  (broken randomisation, logging bug), and the test cannot be trusted
  no matter how good the p-value looks.
"""
import math
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def norm_cdf(x):
    """Standard normal CDF via the error function (stdlib only)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def load_totals(con):
    """Per-variant (visitors, conversions) from experiment_daily."""
    rows = con.execute(
        "SELECT variant, SUM(visitors), SUM(conversions)"
        " FROM experiment_daily GROUP BY variant ORDER BY variant"
    ).fetchall()
    return {v: (n, c) for v, n, c in rows}


def compute(totals):
    """All headline statistics from {(variant): (visitors, conversions)}."""
    n_a, c_a = totals["A"]
    n_b, c_b = totals["B"]
    p_a = c_a / n_a
    p_b = c_b / n_b
    diff = p_b - p_a
    # Two-proportion z-test (pooled standard error).
    p_pool = (c_a + c_b) / (n_a + n_b)
    se_pooled = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = diff / se_pooled
    p_value = 2 * (1 - norm_cdf(abs(z)))
    # 95% CI for the difference (unpooled standard error).
    se_diff = math.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    ci_low, ci_high = diff - 1.96 * se_diff, diff + 1.96 * se_diff
    # SRM: chi-square on the visitor split vs the planned 50/50.
    expected = (n_a + n_b) / 2
    srm_chi2 = (n_a - expected) ** 2 / expected + (n_b - expected) ** 2 / expected
    # 1-degree-of-freedom chi-square p-value, via the normal CDF.
    srm_p = math.erfc(math.sqrt(srm_chi2 / 2)) if srm_chi2 > 0 else 1.0
    significant = p_value < 0.05 and ci_low > 0
    verdict = (
        "SHIP B: variant wins, p < 0.05 and the 95% CI excludes zero."
        if significant
        else "DO NOT SHIP: the result is not significant — keep A, or run longer."
    )
    return {
        "n_a": n_a, "c_a": c_a, "p_a": p_a,
        "n_b": n_b, "c_b": c_b, "p_b": p_b,
        "diff_pp": diff * 100, "uplift_pct": diff / p_a * 100,
        "extra_conversions": c_b - c_a,
        "z": z, "p_value": p_value,
        "ci_low_pp": ci_low * 100, "ci_high_pp": ci_high * 100,
        "srm_chi2": srm_chi2, "srm_p": srm_p,
        "significant": significant, "verdict": verdict,
    }


def format_results(s):
    """Plain-text results file: numbers first, verdict last."""
    return (
        f"A (current button): {s['n_a']} visitors, {s['c_a']} conversions,"
        f" rate {s['p_a'] * 100:.3f}%\n"
        f"B (new button):     {s['n_b']} visitors, {s['c_b']} conversions,"
        f" rate {s['p_b'] * 100:.3f}%\n"
        f"Uplift: {s['diff_pp']:.3f} percentage points"
        f" ({s['uplift_pct']:.1f}% relative),"
        f" +{s['extra_conversions']} conversions over the test\n"
        f"z-statistic: {s['z']:.3f}\n"
        f"p-value (two-sided): {s['p_value']:.5f}\n"
        f"95% CI for the difference: {s['ci_low_pp']:.3f} to"
        f" {s['ci_high_pp']:.3f} percentage points\n"
        f"SRM check: chi2 = {s['srm_chi2']:.3f}, p = {s['srm_p']:.3f}"
        f" (split {s['n_a']}/{s['n_b']}, clean if p > 0.05)\n"
        f"Verdict: {s['verdict']}\n"
    )


def main():
    db = BASE / "data" / "demo.db"
    con = sqlite3.connect(db)
    results = compute(load_totals(con))
    text = format_results(results)
    out = BASE / "outputs" / "ab_results.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
