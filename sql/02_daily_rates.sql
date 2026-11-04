-- A/B test 2: daily conversion rate per variant (long format).
-- Read this before the cumulative view: single days are noisy
-- (A wins 3 of the 14 days, ties one) and no single day decides the test.
SELECT date, variant, visitors, conversions,
       ROUND(1.0 * conversions / visitors, 4) AS conversion_rate
FROM experiment_daily ORDER BY date, variant;
