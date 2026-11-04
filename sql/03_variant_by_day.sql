-- A/B test 3: cumulative (running) rate per variant, day by day.
-- This is the anti-peeking view: the gap wobbles as days accumulate,
-- so calling the test on day 2 or day 3 would have been a guess, not
-- a verdict. Only the full 14 days earn the call in ab_results.txt.
SELECT date, variant,
       SUM(visitors) OVER (PARTITION BY variant ORDER BY date) AS cum_visitors,
       SUM(conversions) OVER (PARTITION BY variant ORDER BY date) AS cum_conversions,
       ROUND(1.0 * SUM(conversions) OVER (PARTITION BY variant ORDER BY date)
                  / SUM(visitors) OVER (PARTITION BY variant ORDER BY date), 4) AS cum_rate
FROM experiment_daily ORDER BY date, variant;
