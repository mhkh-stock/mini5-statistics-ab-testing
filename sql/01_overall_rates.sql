-- A/B test 1: overall conversion rate per variant.
SELECT variant, SUM(visitors) AS visitors, SUM(conversions) AS conversions,
       ROUND(1.0 * SUM(conversions) / SUM(visitors), 4) AS conversion_rate
FROM experiment_daily GROUP BY variant ORDER BY variant;
