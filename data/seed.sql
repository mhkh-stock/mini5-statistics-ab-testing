-- Mini #5 seed data. SAMPLE only, generated deterministically:
-- Python random.Random(7), one binomial draw per variant per day
-- (control p = 0.12, variant p = 0.145), visitors fixed per day and
-- identical for both variants (balanced allocation: 4,000 each).
-- Daily rows below are the draws; re-running the generator reproduces
-- them exactly. The device table allocates each variant's totals
-- 60/40 by visitors (mobile/desktop) and splits conversions in the
-- same proportion, so device totals reconcile exactly to daily totals.
INSERT INTO experiment_daily VALUES
  ('2026-10-01','A',250,27), ('2026-10-01','B',250,39),
  ('2026-10-02','A',260,32), ('2026-10-02','B',260,26),
  ('2026-10-03','A',340,30), ('2026-10-03','B',340,48),
  ('2026-10-04','A',350,34), ('2026-10-04','B',350,52),
  ('2026-10-05','A',270,51), ('2026-10-05','B',270,46),
  ('2026-10-06','A',280,27), ('2026-10-06','B',280,37),
  ('2026-10-07','A',290,29), ('2026-10-07','B',290,45),
  ('2026-10-08','A',250,31), ('2026-10-08','B',250,25),
  ('2026-10-09','A',260,34), ('2026-10-09','B',260,34),
  ('2026-10-10','A',340,40), ('2026-10-10','B',340,55),
  ('2026-10-11','A',350,37), ('2026-10-11','B',350,51),
  ('2026-10-12','A',270,36), ('2026-10-12','B',270,38),
  ('2026-10-13','A',280,27), ('2026-10-13','B',280,46),
  ('2026-10-14','A',210,32), ('2026-10-14','B',210,34);
INSERT INTO experiment_device VALUES
  ('A','mobile',2400,280), ('A','desktop',1600,187),
  ('B','mobile',2400,346), ('B','desktop',1600,230);
