-- A/B test 4: conversion rate per variant per device.
-- B wins on both devices, so the overall win is not a mix artifact
-- (a win driven by one device while losing on the other would be).
-- Device totals reconcile exactly to query 01; run_analysis.py asserts it.
SELECT variant, device, visitors, conversions,
       ROUND(1.0 * conversions / visitors, 4) AS conversion_rate
FROM experiment_device ORDER BY variant, device;
