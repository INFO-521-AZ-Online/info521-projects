# Part 2 — From Inference to Discovery (Modules 5–7)

*The second half of the course project, beginning at the midpoint, due Week 7.5.*

Part 2 continues the *same* clinical cohort from Part 1 and extends it from
prediction into discovery. Two things expand at once: the **method** (regression →
classification → unsupervised) and the **feature space** (single predictor → the
six-feature non-BP set). It is organized as **two thematic gates plus the synthesis**.

## Milestones

**Gate A — Supervised** (predict the hypertension label from the non-BP features)

1. [**2.1 Approximate Bayesian inference** (M5)](2.1-approximate-inference.qmd) —
   Bayesian logistic regression; from-scratch log-posterior / gradient / Hessian
   (gradient-checked), Newton–Raphson (MAP), Laplace approximation, Metropolis
   sampler; MAP/Laplace/Metropolis mapped to P1's point/likelihood/posterior.
   Gated by **Checkpoint quiz 2.1**.
2. [**2.2 Classification** (M6)](2.2-classification.qmd) — from-scratch soft-margin
   SVM (primal hinge + L2, Pegasos), precision/recall/F1, the dual + kernel trick
   (conceptual), probabilistic-vs-margin showdown on one split.

**Gate B — Unsupervised** (drop the labels; find structure)

3. [**2.3 Clustering** (M6)](2.3-clustering.qmd) — from-scratch k-means, random
   restarts for local minima, K selection (elbow / silhouette), and the
   cluster-vs-held-out-label reveal. Gated by **Checkpoint quiz 2.3**.
4. [**2.4 Dimensionality reduction** (M7)](2.4-dimensionality-reduction.qmd) —
   from-scratch PCA (covariance/SVD), variance explained, biplot, and the k-means
   clusters re-viewed in PC space.

**Synthesis**

5. [**2.5 Synthesis**](2.5-synthesis.qmd) — one narrative across the whole semester
   on one cohort; supervised vs. unsupervised argument; structured peer review.

## The additive bridge

Part 1 ended on a closed-form conjugate Gaussian posterior. Part 2 breaks it
deliberately:

1. **Approximate Bayesian inference (M5).** Binarize systolic BP into a
   **hypertension** label (ACC/AHA: SBP ≥ 130 or DBP ≥ 80) and predict it from the
   **non-BP** features — the blood-pressure columns are excluded so the label can't
   leak into its own predictors. A Bayesian **logistic regression** model has **no
   conjugate posterior** — so you implement, from scratch: Newton–Raphson (MAP),
   the Laplace approximation, and a Metropolis sampler. Compare what each buys you.
2. **Classification (M6).** The same binary label is now an SVM target. Soft-margin
   primal (with the dual and kernel trick derived conceptually). Evaluate with
   precision / recall / F1. Contrast the discriminative SVM with the probabilistic
   classifier from step 1.
3. **Clustering (M6).** Drop the labels. Implement k-means from scratch on the
   six-feature set; address local minima (restarts) and model selection (choosing
   K). Do the discovered clusters relate to the hypertension label?
4. **Dimensionality reduction (M7).** PCA from scratch on the features; visualize
   the cohort in 2-D; feed components into the clustering and discuss.

## Gates & bundle (specs)

The Part 2 bundle is **Satisfactory** when:

- **Gate A — Supervised:** 2.1 **and** 2.2 Satisfactory, **and Checkpoint 2.1**
  (Newton–Raphson update) passed.
- **Gate B — Unsupervised:** 2.3 **and** 2.4 Satisfactory, **and Checkpoint 2.3**
  (k-means objective / PCA) passed.
- **Synthesis:** 2.5 Satisfactory (structured peer review completed).

See `../GRADING.md` for the specs mechanics. The checkpoint quizzes that gate these milestones run on D2L; each is due the week before its milestone.

## Play, extended

- A held-out **prediction round** on the binary outcome (compare SVM vs. Bayesian
  logistic regression on the same split).
- A **cluster-vs-label reveal**: do unsupervised subgroups recover clinical
  hypertension strata you never showed the algorithm?
- PCA **biplot exploration**: which features drive the principal axes?

## Carry-over outcomes

The same plumbing applies: `info521.data.hypertension(ds)` provides the
leakage-safe Gate A label (ACC/AHA hypertension); `load_clinical()` returns the
feature matrix with the blood-pressure columns (`sbp`, `dbp`) excluded, so the
Gate A/B feature set is non-BP by construction; `checks.expect_gradient` verifies
the 2.1 gradient. No estimators are added to the library — k-means, PCA, SVM, and
the samplers are all student-implemented.
