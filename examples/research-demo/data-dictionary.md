# Synthetic data dictionary, version 1.0.0

The records were invented for this teaching bundle. There are no people or
personal identifiers behind them. No field is a validated instrument.

| Column | Type and unit | Teaching range | Meaning | Missingness |
| --- | --- | --- | --- | --- |
| participant_id | string | unique S01–S12 | invented record key | forbidden |
| study_hours | number, hours | 0–24 | invented exposure variable | forbidden |
| baseline | number, points | 0–100 | invented baseline covariate | forbidden |
| score | number, points | 0–100 | invented outcome | forbidden |
| quality_flag | string | none, A, B | invented branching labels | forbidden |

The parser rejects invalid, nonfinite, out-of-range and duplicate values. No
missing-data method is implemented. A/B labels illustrate alternative sample
rules, without claiming they are scientifically justified for a real study.
The CSV is immutable input; generated derivatives go into `outputs/`. This
folder contains code under MIT and synthetic records under CC0.
