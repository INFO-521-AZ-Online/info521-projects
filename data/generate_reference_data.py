"""Generate the synthetic clinical *reference* dataset shipped with the starter.

This dataset is the OFFLINE FALLBACK for the deployed NHANES 2021-2022 extract
(see ../instructor/dataset-curation.md). It is a **contract mirror**, not a
demographic mirror: it honors the exact column contract that
``info521.data.load_clinical`` expects -- the same eight columns in the same
order, ``sbp`` as the continuous target and ``dbp`` reserved for the Part 2
hypertension label -- so ``load_clinical(path=...)``, ``binarize``, and
``hypertension(ds)`` all behave identically on it as on the real data. It is
SYNTHETIC and must never be presented to students as real clinical data.

NOTE: age is intentionally YOUNG-SKEWED (unlike the roughly-flat real NHANES
adult age distribution) so the sparse-upper-tail lesson -- predictive uncertainty
widening where data is thin (milestone 1.2) -- stays visible. That is the one place
this file deliberately departs from the real data; everything else mirrors it.

Construction: a **Gaussian copula**. We draw a latent multivariate normal with the
target 8x8 correlation matrix (taken from the deployed NHANES QA), then push each
margin through its target marginal -- a young-skewed Beta for age, rescaled
normals (mean/SD) for the rest. Linear (normal) margins preserve the latent
correlations exactly, so the target correlation structure is reproduced directly.
Real blood pressure is right-skewed, so symmetric-normal sbp/dbp margins at the
exact NHANES means over-shoot the 130/80 hypertension prevalence; we set the
SBP/DBP *level* ~1.5 mmHg below the NHANES means to recover ~0.388 (see MARGINS).
The realized means/SDs still sit well inside the QA's +/- 2 windows. (A
latent-factor build would instead under-shoot, because the young-skewed age drags
the conditional SBP mean down, and would need the level lifted the other way.)

Run:  python generate_reference_data.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import beta, norm

SEED = 521
N = 2000
OUT = "clinical_reference.csv"

# Column order == the deployed NHANES contract. sbp = target; dbp = reserved.
COLS = ["age", "bmi", "waist", "chol", "hdl", "hba1c", "sbp", "dbp"]

# Target marginals (mean, sd) from the deployed NHANES QA. age is handled
# separately (young-skewed Beta on [18, 79]); the rest are rescaled normals.
#
# sbp/dbp level note: real blood pressure is right-skewed, so symmetric-normal
# margins at the exact NHANES means (121.5 / 74.7) put too much mass past the
# 130/80 thresholds and over-shoot prevalence (~0.437). We set the SBP/DBP level
# ~1.5 mmHg below the NHANES means to recover the ~0.388 prevalence; the realized
# means (~120.3 / ~73.1) and SDs still sit well inside the QA's +/- 2 windows.
MARGINS = {
    "bmi": (29.0, 7.0),
    "waist": (99.0, 16.0),
    "chol": (190.0, 40.0),
    "hdl": (54.0, 15.0),
    "hba1c": (5.7, 1.0),
    "sbp": (120.0, 17.2),
    "dbp": (73.2, 10.8),
}

# Clinical floors -- guard against absurd lower-tail draws (touch <~1% of rows).
FLOORS = {
    "bmi": 13.0, "waist": 55.0, "chol": 90.0, "hdl": 15.0,
    "hba1c": 3.5, "sbp": 75.0, "dbp": 38.0,
}

# Age: young-skewed Beta over the adult range (sparse upper tail).
AGE_LO, AGE_HI = 18.0, 79.0
AGE_BETA_A, AGE_BETA_B = 2.0, 3.0

# Target 8x8 correlation matrix (row/col order == COLS), from the NHANES QA.
TARGET_CORR = np.array([
    # age    bmi   waist  chol   hdl   hba1c  sbp    dbp
    [1.00,  0.06,  0.22,  0.09,  0.11,  0.27,  0.38,  0.07],  # age
    [0.06,  1.00,  0.90, -0.02, -0.28,  0.20,  0.04,  0.21],  # bmi
    [0.22,  0.90,  1.00, -0.02, -0.34,  0.26,  0.12,  0.23],  # waist
    [0.09, -0.02, -0.02,  1.00,  0.27, -0.01,  0.09,  0.19],  # chol
    [0.11, -0.28, -0.34,  0.27,  1.00, -0.18,  0.04, -0.02],  # hdl
    [0.27,  0.20,  0.26, -0.01, -0.18,  1.00,  0.17,  0.09],  # hba1c
    [0.38,  0.04,  0.12,  0.09,  0.04,  0.17,  1.00,  0.65],  # sbp
    [0.07,  0.21,  0.23,  0.19, -0.02,  0.09,  0.65,  1.00],  # dbp
])

# QA acceptance targets (mirrors the build_nhanes QA + the task spec).
HTN_PREV_TARGET = 0.388
CORR_CHECKS = [("sbp", "dbp", 0.65), ("age", "sbp", 0.38),
               ("bmi", "waist", 0.90), ("waist", "hdl", -0.34)]


def _nearest_psd_correlation(C: np.ndarray) -> np.ndarray:
    """Symmetrize, clip negative eigenvalues to >=0, renormalize to unit diagonal."""
    C = (C + C.T) / 2.0
    vals, vecs = np.linalg.eigh(C)
    vals = np.clip(vals, 1e-8, None)
    C = (vecs * vals) @ vecs.T
    d = np.sqrt(np.diag(C))
    C = C / np.outer(d, d)
    C = (C + C.T) / 2.0
    np.fill_diagonal(C, 1.0)
    return C


def generate() -> np.ndarray:
    rng = np.random.default_rng(SEED)
    C = _nearest_psd_correlation(TARGET_CORR)

    # Latent standard normals carrying the target correlation structure.
    Z = rng.multivariate_normal(np.zeros(len(COLS)), C, size=N)
    col = {}

    # age: young-skewed Beta via the copula (sparse upper tail).
    u_age = norm.cdf(Z[:, COLS.index("age")])
    col["age"] = AGE_LO + (AGE_HI - AGE_LO) * beta.ppf(u_age, AGE_BETA_A, AGE_BETA_B)

    # remaining margins: rescaled normals (linear -> correlations preserved).
    for name, (mu, sd) in MARGINS.items():
        col[name] = mu + sd * Z[:, COLS.index(name)]

    # clinical floors (negligible mass; keeps every value physically sensible).
    for name, lo in FLOORS.items():
        col[name] = np.maximum(col[name], lo)
    col["age"] = np.clip(col["age"], AGE_LO, AGE_HI)

    return np.column_stack([col[c] for c in COLS])


def qa(M: np.ndarray) -> None:
    """Print the NHANES-style QA block, then assert acceptance (raise on miss)."""
    df = pd.DataFrame(M, columns=COLS)
    n = len(df)
    sbp = df["sbp"].to_numpy()
    dbp = df["dbp"].to_numpy()
    htn = (sbp >= 130) | (dbp >= 80)
    corr = df.corr()

    print("\n" + "=" * 70)
    print("QA SUMMARY  --  synthetic offline fallback (contract mirror)")
    print("=" * 70)
    print(f"N retained                 : {n}")
    print(f"age range                  : {df['age'].min():.0f} - {df['age'].max():.0f} yr")
    print(f"sbp mean (SD)              : {sbp.mean():.2f} ({sbp.std(ddof=1):.2f}) mmHg")
    print(f"dbp mean (SD)              : {dbp.mean():.2f} ({dbp.std(ddof=1):.2f}) mmHg")
    print(f"hypertension prevalence    : {htn.mean():.3f}   (rule: SBP>=130 OR DBP>=80)")
    print("\nper-column missingness (should all be 0):")
    miss = df[COLS].isna().sum()
    for c in COLS:
        print(f"  {c:<6}: {int(miss[c])}")
    print("\n8x8 correlation matrix:")
    with pd.option_context("display.float_format", lambda v: f"{v:6.3f}"):
        print(corr.to_string())
    print("=" * 70)

    # --- acceptance asserts ----------------------------------------------
    def check(ok: bool, msg: str) -> None:
        if not ok:
            raise AssertionError(f"QA acceptance failed: {msg}")

    check(list(df.columns) == COLS, f"column order {list(df.columns)} != {COLS}")
    check(int(miss.sum()) == 0, f"missingness present: {miss.to_dict()}")
    check(abs(sbp.mean() - 121.5) <= 2.0, f"sbp mean {sbp.mean():.2f} not within 121.5 +/- 2")
    check(abs(sbp.std(ddof=1) - 17.2) <= 2.0, f"sbp SD {sbp.std(ddof=1):.2f} not within 17.2 +/- 2")
    check(abs(dbp.mean() - 74.7) <= 2.0, f"dbp mean {dbp.mean():.2f} not within 74.7 +/- 2")
    check(abs(dbp.std(ddof=1) - 10.8) <= 2.0, f"dbp SD {dbp.std(ddof=1):.2f} not within 10.8 +/- 2")
    for a, b, target in CORR_CHECKS:
        got = corr.loc[a, b]
        check(abs(got - target) <= 0.06, f"corr({a},{b})={got:.3f} not within {target} +/- 0.06")
    check(abs(htn.mean() - HTN_PREV_TARGET) <= 0.03,
          f"hypertension prevalence {htn.mean():.3f} not within {HTN_PREV_TARGET} +/- 0.03")
    print("All QA acceptance checks PASSED.")


def main() -> int:
    M = generate()
    qa(M)  # asserts before we overwrite the shipped CSV
    header = ",".join(COLS)
    np.savetxt(OUT, M, delimiter=",", header=header, comments="", fmt="%.4f")
    print(f"\nWrote {OUT}: {M.shape[0]} rows x {M.shape[1]} cols")
    print(f"  column order: {', '.join(COLS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
