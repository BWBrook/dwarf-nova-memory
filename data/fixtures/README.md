# Handwritten synthetic format fixture

`synthetic_photometry.csv` contains six invented measurements solely to exercise
the normalized table format. It is not a real star, an archive export, a complete
cycle, or a suitable input for scientific fitting. A faint limit is stored as a
limit, with the exact magnitude left empty. Here `14.0` means flux below the
associated threshold, equivalently a magnitude numerically greater than 14.0.

All timestamps are relative simulation days. No UTC, HJD or BJD conversion has
been applied or implied. Run `python scripts/validate_photometry.py
data/fixtures/synthetic_photometry.csv` from the project root.
