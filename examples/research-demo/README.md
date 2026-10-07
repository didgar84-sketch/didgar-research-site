# Auditable research mini-project

All 12 records are **synthetic**. No participants, observed findings, actual peer
reviews or publication acceptances are represented. The code is a teaching
example, not mature JOSS-eligible software or a validated statistical package.

## Run the computations

Use Python 3.10 or later. From this folder run:

```sh
python3 research.py
python3 test_examples.py
python3 equivalence.py
```

No external Python packages are required for these commands. Open
`outputs/index.html` to inspect fresh results. The output comprises a summary,
all six descriptive OLS paths, an SVG chart, a file hash and two separate normal
TOST scenarios. The 12 scores sum to 808, giving mean 67.333333 points and sample
SD approximately 9.128709. These are synthetic calculations, not student findings.

## Data and choices

`data-dictionary.md` defines every field. Three illustrative inclusion rules
(all; exclude A; exclude A and B) are crossed with unadjusted and baseline-adjusted
OLS. Sample counts are 12/12, 10/10 and 8/8. The A/B flags are invented labels:
they do not justify exclusions in a real project. Baseline adjustment changes the
coefficient's interpretation and requires its own scientific rationale.

This six-path illustration does not implement specification-curve inference,
confidence intervals, cluster corrections, a power calculation or causal
identification. Report all paths rather than selecting a preferred coefficient.
Tests use independently known lines/planes, an independent normal-tail formula,
invalid-input cases and output agreement.

## Separate equivalence example

`equivalence.py` uses estimate 0.20, SE 0.15 or 1.0, and teaching bounds ±0.5. It
is **not** an analysis of the CSV. With SE 0.15, CI90 is approximately
[−0.046728, 0.446728] and p_TOST approximately 0.022750. This supports equivalence
under the stated normal model while CI95 includes zero. SE 1.0 is inconclusive.
Real bounds must be justified prospectively, and the estimator, distribution,
degrees of freedom and dependence need design-specific treatment.

## Optional Quarto document

Install Quarto and a suitable Jupyter Python kernel separately, then use:

```sh
quarto render manuscript.qmd --to html
quarto render manuscript.qmd --to docx
quarto render manuscript.qmd --to pdf
```

Rendering requires the appropriate environment. PDF also needs the configured
XeLaTeX engine; SVG support, fonts and Word styles require format-specific
checking. The supplied release verified Python calculations, **not** a Quarto,
Word or PDF rendering. Persian/Arabic RTL documents need appropriate language,
font and direction settings and separate equation/table checks. `mean_score`
is calculated before its inline reference; no cached result is claimed as fresh.

## Other teaching documents

The mock Registered Reports protocol/response, publication-thesis architecture
and Data Descriptor outline show how to document decisions. They are independent
exercises, not evidence that this mini-project received review or meets a journal's
submission requirements. The guide workbooks provide the corresponding exercises
in Persian, English and Arabic.

Code in this mini-project is MIT licensed; its invented CSV records are released
under CC0. Third-party references and the institute's branding are not included in
those grants. AI assistance was used to prepare this example, followed by source
checks and the documented executable tests; specialist peer review is not claimed.
