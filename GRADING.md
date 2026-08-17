# Grading — Specs Model

Both projects use specifications grading. There are no points on milestones; each
is judged against published criteria as **Satisfactory** or **Not-Yet**.

## Milestones

- Every milestone lists its Satisfactory criteria at the top of the notebook.
  All criteria must be met — it is all-or-nothing, not partial credit.
- A **Not-Yet** returns with targeted feedback and **one revise cycle** back to
  Satisfactory. (Set a revise window that fits your cadence, e.g. one week.)
- A project is complete when all its milestones are Satisfactory **and** all its
  checkpoints are passed.

## Checkpoints

- Short open-book **D2L quizzes** (about 20 to 30 minutes), one per module, on
  that module's derivations. Mostly auto-graded, plus two or three short written
  responses.
- **Satisfactory** requires the auto-graded pass bar (80%) and Satisfactory
  written responses; written responses carry **one revision** cycle, matching
  the milestone policy.
- Each quiz is due the week its module is taught and **gates the milestone due
  the following week**, so the gate resolves before the gated work is due.
- The coding verification that used to sit beside these derivations lives in
  Homework Units 1, 3, and 4 and in milestones 2.1, 2.3, and 2.4 (see
  info521-homeworks-2026/CHECKPOINT_HOMEWORK_MERGE.md). Nothing is assessed
  twice.
- A milestone cannot be marked Satisfactory until its gating checkpoint quiz is
  passed.

## From scratch, defined

Implement every estimator yourself in NumPy/SciPy: no scikit-learn, no
off-the-shelf solver, sampler, or metric function, here or anywhere in this
project. Your own prior work is different. Code you wrote and certified in a
homework unit may be imported or copied into any milestone, and reusing it is
encouraged: the homework certified that your components work; the milestone
grades what you build with them. (The reverse also holds: no milestone
requires a homework unit to have been passed. A student who skipped a unit
can always write the code fresh inside the milestone.)

Milestones 2.2 to 2.4 (SVM, k-means, PCA) have no homework rehearsal:
modules 6 and 7 run in weeks 6 to 7.5, and those notebooks scaffold their
own implementations. That asymmetry is by design.

## One project, two parts

The course has **one project**, in two parts on one dataset. Part 1, *One Problem, Three
Lenses* (milestones 1.1 to 1.4), is due **Week 5, the midpoint**. Part 2, *From Inference
to Discovery* (milestones 2.1 to 2.5), is due **Week 7.5**. Gated as below.

All five checkpoint quizzes are required as the Checkpoints category, and each gates the
milestone it is named for.

## Weighting

Part 2 is **not** weighted more heavily than Part 1: specs grading already enforces that
Part 2 mastery presupposes
Part 1's foundations, so there is no need to also price that into a weight.

Revise-and-resubmit is the safety net; it replaces the former "final replaces
lowest midterm" rule cleanly.

> The exact contribution of each project to the final grade depends on how these
> fold into the broader course scheme (homework units, peer-engagement loops).
> Set that in the syllabus; this file governs the *mechanics*, not the percentages.

## Bundling (suggested)

- **Part 1 bundle:** 1.1, 1.2, 1.3, 1.4 all Satisfactory + Checkpoint quizzes 1.1 to 1.3
  passed. Due at the midpoint (Week 5).
- **Part 2 bundle:** two thematic gates + the synthesis, all Satisfactory, plus Checkpoint
  quizzes 2.1 and 2.3 passed:
  - **Gate A — Supervised:** 2.1 (approximate inference) + 2.2 (classification)
    Satisfactory, **and Checkpoint 2.1** (Newton–Raphson update) passed.
  - **Gate B — Unsupervised:** 2.3 (clustering) + 2.4 (dimensionality reduction)
    Satisfactory, **and Checkpoint 2.3** (k-means objective / PCA) passed.
  - **Synthesis:** 2.5 Satisfactory, with its structured peer review completed.
- **The project** is Satisfactory when both part bundles are.

## Academic integrity note

Homework is open-book and AI-permitted in this course, so it certifies "can
produce with help." The checkpoint quizzes are delivered online and are also
open-book, so they do **not** certify unaided derivation, and this document no
longer claims they do. What they certify is narrower and still worth having:
that a student can produce the derivation, state what it depends on, and connect
it to their own project results before the milestone that uses it comes due.

The load-bearing parts are the written responses, because they ask about the
student's own fits and results. That tie to their own project is what makes the
answer theirs rather than generic. Keep it intact if you adjust the model.
