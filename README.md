# INFO 521: Projects

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21971137.svg)](https://doi.org/10.5281/zenodo.21971137) [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

If using these materials, cite the following: 
>Chism, G. (2026). INFO 521: Machine Learning Foundations — Course Project (Version v1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21971137

The course's one two-part project, which replaces the former midterms and final.
Part 1 is due at the term midpoint (Week 5); Part 2 closes the term (Week 7.5). The
exams' applied, integrative, and synthesis outcomes live in the project; the
derivation outcomes are short open-book **checkpoint quizzes on D2L**, each due the
week before the milestone it gates. Homework is the method workshop that certifies
each estimator before the milestone that applies it (the reuse rule below).

This repo is **public and student-safe by construction**: it carries no answers, no
quiz content, and no reference solutions. Those live in the private
`info521-homeworks-2026` repo. Students do not clone this repo either; they receive
a generated template repo through Classroom 50 (see below).

**Instructors: the full setup path is `INSTRUCTOR_CHECKLIST.md` in the private
homeworks repo.**

## The arc

**One clinical dataset carries the whole semester.** A single continuous
prediction problem is examined through progressively richer lenses, then extended
from prediction into discovery.

### Part 1: One Problem, Three Lenses (Modules 1 to 4)

Same dataset, same single predictor (age → SBP), three accreting lenses:

| Milestone | Lens | Gated by |
|---|---|---|
| 1.1 | Least squares (design matrix, CV, L2) | Checkpoint quiz 1.1, normal equations |
| 1.2 | Maximum likelihood (Gaussian noise, predictive variance) | Checkpoint quiz 1.2, MLE for **w** |
| 1.3 | Bayesian (conjugate posterior, credible intervals) | Checkpoint quiz 1.3, posterior of a conjugate pair |
| 1.4 | Synthesis: all three lenses, side by side | (structured peer review) |

### Part 2: From Inference to Discovery (Modules 5 to 7)

Binarize the outcome → conjugacy breaks → approximate inference (Newton–Raphson,
Laplace, MCMC) → classification (SVM) → clustering (k-means) → dimensionality
reduction (PCA), now across the **full** non-BP feature set.

| Milestone | Lens | Gated by |
|---|---|---|
| 2.1 | Approximate inference (Newton–Raphson, Laplace, Metropolis) | Checkpoint quiz 2.1, Newton–Raphson update |
| 2.2 | Classification (soft-margin SVM from scratch) | Gate A with 2.1 |
| 2.3 | Clustering (k-means, WCSS, restarts) | Checkpoint quiz 2.3, k-means objective / PCA |
| 2.4 | Dimensionality reduction (PCA, biplot) | Gate B with 2.3 |
| 2.5 | Synthesis: one cohort, a whole semester | (structured peer review) |

## Assessment model

Specs grading. Each milestone is **Satisfactory / Not-Yet** with one revise cycle.
Each checkpoint is an open-book D2L quiz: the auto-graded portion resolves on
submission, and its written responses are Satisfactory / Not-Yet with one revise
cycle. A milestone reaches Satisfactory only once its checkpoint quiz is passed.
The two parts are co-equal summative halves. See `GRADING.md`.

## Ground rules for students

- Implement every estimator **from scratch** in NumPy/SciPy. No scikit-learn or
  other off-the-shelf solvers. From scratch rules out libraries, never your own
  prior work: code you built and certified in a homework unit may be copied or
  imported into any milestone, and reusing it is encouraged (`GRADING.md`,
  "From scratch, defined").
- The `info521` library is **plumbing only**: data, plotting, self-checks. It
  contains no fitting routines by design.

## Repo layout

```
project-1/         four .qmd milestone notebooks (1.1 to 1.4)
project-2/         five .qmd milestone notebooks (2.1 to 2.5)
common/info521/    plumbing library (data, plotting, checks), no estimators
data/              curated NHANES 2021-2022 extract + builder + synthetic fallback
pdfs/              generated D2L briefs: 9 milestone briefs + 2 part overviews
                   (PDF, DOCX, HTML each); rebuild with tools/build_milestones.py
                   and tools/build_overviews.py
tools/             the brief builders and tools/make_project_template.py, which
                   assembles the student template repo into build/ from an explicit
                   allowlist and verifies nothing answer-bearing got in
build/             generated student template (gitignored; rebuild at will)
environment.yml, pyproject.toml   the pinned environment (Python 3.11, numpy 2.1.x)
(checkpoint quizzes, keys, and reference solutions live in the private homeworks repo)
```

## The dataset

The deployed default is a curated **NHANES 2021-2022** extract
(`data/nhanes_2021_2022.csv`, N = 5,102), built from the `_L` cycle files by
`data/build_nhanes.py`. Blood pressure comes from the **BPXO** oscillometric
series. Six leakage-safe non-BP features (`age, bmi, waist, chol, hdl, hba1c`)
predict systolic BP in Part 1; `dbp` is reserved to build the Part 2 hypertension
label under the ACC/AHA rule (SBP ≥ 130 or DBP ≥ 80), prevalence 38.8%. A
reproducible synthetic dataset (`data/clinical_reference.csv`, N = 2,000) mirrors
the loader's API exactly and is the offline fallback.

## Quick start

Python 3.11 with numpy 2.1.x. Python 3.14 is not supported (C-ABI/numpy
incompatibility).

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e .                      # installs the info521 plumbing package
quarto render project-1/1.1-least-squares.qmd
```

Quarto must be installed separately (https://quarto.org); it is not a Python
package. `environment.yml` remains available if you prefer conda.

## Building the student template

```bash
python tools/make_project_template.py
```

Assembles `build/projects-template/` (a fresh git repo) from an explicit allowlist,
then re-verifies: exactly nine milestone notebooks, zero checkpoint files, nothing
answer-bearing. Push it to your org as a **public** repo flagged as a template; the
instructor checklist covers the Classroom 50 wiring.

## Instructor decisions baked in

Dataset curation, peer-review cadence, checkpoint-quiz design, and play-artifact
parameters are recorded in the private homeworks repo (`projects-instructor/`).
Adjust there.
