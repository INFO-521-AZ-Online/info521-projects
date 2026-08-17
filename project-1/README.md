# Part 1 — One Problem, Three Lenses (Modules 1–4)

*The first half of the course project, due Week 5, the midpoint.*

One clinical dataset, one prediction problem (age → systolic blood pressure),
examined through three accreting lenses and then synthesized.

## Milestones

1. **1.1 Least Squares** (M1–M2) — design matrix, normal equations, K-fold CV, L2.
   Play artifact: a 3×3 bias–variance sweep over polynomial orders {1, 3, 9} and
   λ ∈ {1e-3, 1e-1, 1e1}. Gated by Checkpoint quiz 1.1 (due Week 2; milestone due Week 3).
2. **1.2 Maximum Likelihood** (M3) — Gaussian-noise generative model, MLE for **w**
   (shown numerically equal to the 1.1 OLS fit), $\hat\sigma^2$, predictive error
   bars. Play artifact: where the model is least sure, and why. Gated by
   Checkpoint quiz 1.2 (due Week 3; milestone due Week 4).
3. **1.3 Bayesian** (M4) — Gaussian prior, conjugate posterior, posterior-predictive
   credible intervals. Play artifact: prior-strength and data-amount sweeps
   showing collapse toward the MLE. Gated by Checkpoint quiz 1.3 (due Week 4; milestone due Week 5).
4. **1.4 Synthesis** — one panel, three lenses; argued compare-and-contrast;
   reproducible end-to-end. Structured peer review.

## Through-line

Part 1 stays **single-predictor polynomial** the whole way (model order is the
only complexity knob, exactly the Module 1–2 lecture arc). Expanding to the full
multivariate feature set is one of the things **Part 2 adds**.

## Satisfactory

Each notebook states its own criteria at the top. The project is complete when
1.1–1.4 are all Satisfactory and Checkpoint quizzes 1.1 to 1.3 are passed. See `../GRADING.md`.

## Bridge to Part 2

1.3 leans entirely on conjugacy (closed-form Gaussian posterior). Part 2 opens
by binarizing systolic BP into a **hypertension** label (ACC/AHA: SBP ≥ 130 or
DBP ≥ 80) — conjugacy breaks, the posterior goes intractable, and approximate
inference becomes necessary. The same binary label, predicted from the **non-BP**
features (the blood-pressure columns are held out to avoid label leakage), then
drives classification; dropping it entirely motivates clustering and PCA.
