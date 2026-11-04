-- Mini #5 demo schema. Two tables, both SAMPLE data:
-- experiment_daily: one row per day per variant (the experiment itself).
-- experiment_device: the same totals split by device (a segment summary,
-- not a second experiment). The runner rebuilds data/demo.db from this
-- schema plus seed.sql on every run.
CREATE TABLE experiment_daily (
  date TEXT NOT NULL,
  variant TEXT NOT NULL CHECK (variant IN ('A', 'B')),
  visitors INTEGER NOT NULL CHECK (visitors > 0),
  conversions INTEGER NOT NULL CHECK (conversions >= 0),
  PRIMARY KEY (date, variant)
);
CREATE TABLE experiment_device (
  variant TEXT NOT NULL CHECK (variant IN ('A', 'B')),
  device TEXT NOT NULL CHECK (device IN ('mobile', 'desktop')),
  visitors INTEGER NOT NULL CHECK (visitors > 0),
  conversions INTEGER NOT NULL CHECK (conversions >= 0),
  PRIMARY KEY (variant, device)
);
