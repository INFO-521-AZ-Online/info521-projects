"""Data loading plumbing.

Returns plain NumPy arrays so students build design matrices themselves. No
preprocessing decisions (scaling, splitting, polynomial expansion) are made for
them -- those are graded skills.

The deployed default dataset is the curated NHANES 2021-2022 extract built by
``data/build_nhanes.py``; the shipped synthetic CSV remains an offline fallback.
"""

from __future__ import annotations

import os
import numpy as np

_HERE = os.path.dirname(__file__)
_DATA_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "data"))
# Deployed default: curated NHANES 2021-2022 (built by data/build_nhanes.py).
_DEFAULT_CSV = os.path.join(_DATA_DIR, "nhanes_2021_2022.csv")
# Offline fallback: the reproducible synthetic reference dataset.
_SYNTHETIC_CSV = os.path.join(_DATA_DIR, "clinical_reference.csv")

# Column contract for the deployed dataset.
_TARGET = "sbp"    # continuous target: systolic blood pressure (mmHg)
_RESERVED = "dbp"  # diastolic BP: RESERVED for the Part 2 label, never a feature/target


def load_clinical(path: str | None = None):
    """Load the clinical dataset.

    Parameters
    ----------
    path : str, optional
        CSV path. Defaults to the deployed NHANES 2021-2022 extract
        (``data/nhanes_2021_2022.csv``, built by ``data/build_nhanes.py``). For
        offline work, point this at the shipped synthetic reference fallback,
        e.g. ``load_clinical(path="data/clinical_reference.csv")``.

    Returns
    -------
    dict with keys:
        'X'        : (n, d) ndarray of feature columns (target AND dbp excluded)
        'y'        : (n,)   ndarray, continuous target -- systolic BP ('sbp')
        'dbp'      : (n,) ndarray or None -- the RESERVED diastolic-BP column.
                     Used only to build the Part 2 hypertension label (see
                     `hypertension`); never a feature, never the target. None if
                     the loaded CSV has no 'dbp' column (e.g. the synthetic CSV).
        'features' : list[str], length d, feature column names
        'primary'  : str, the recommended single predictor for Part 1 ('age')
        'target'   : str, the target name ('sbp')

    Notes
    -----
    Contract: the CSV has a header row and a continuous target column named
    'sbp'. A column named 'dbp', if present, is RESERVED -- excluded from both the
    feature matrix and the target, and surfaced separately so Part 2 can build
    the leakage-safe hypertension label without leaking blood pressure into the
    feature set. A column named 'age' serves as the Part 1 primary predictor.
    """
    if path is None:
        if not os.path.exists(_DEFAULT_CSV):
            raise FileNotFoundError(
                "Deployed dataset not found:\n"
                f"  {_DEFAULT_CSV}\n"
                "Build it first:\n"
                "  python data/build_nhanes.py\n"
                "Or, for offline work, load the synthetic reference fallback:\n"
                f"  load_clinical(path={_SYNTHETIC_CSV!r})"
            )
        path = _DEFAULT_CSV

    with open(path) as fh:
        header = fh.readline().strip().split(",")
    M = np.genfromtxt(path, delimiter=",", skip_header=1)

    if _TARGET not in header:
        raise ValueError(
            f"dataset contract violated: expected a '{_TARGET}' target column in "
            f"{path} (header was {header})"
        )
    target_idx = header.index(_TARGET)
    dbp_idx = header.index(_RESERVED) if _RESERVED in header else None

    excluded = {target_idx}
    if dbp_idx is not None:
        excluded.add(dbp_idx)
    feature_idx = [i for i in range(len(header)) if i not in excluded]
    features = [header[i] for i in feature_idx]

    return {
        "X": M[:, feature_idx],
        "y": M[:, target_idx],
        "dbp": M[:, dbp_idx] if dbp_idx is not None else None,
        "features": features,
        "primary": "age" if "age" in features else features[0],
        "target": _TARGET,
    }


def primary_predictor(ds) -> np.ndarray:
    """Return the single primary-predictor column (Part 1 works in 1-D)."""
    return ds["X"][:, ds["features"].index(ds["primary"])]


def binarize(y: np.ndarray, threshold: float | None = None):
    """Binarize a continuous target by a scalar threshold (generic median split).

    Returns (labels, threshold). Default threshold is the median (balanced
    split). This is a *framing* helper, not a model. For the Part 2
    conjugacy-break bridge use `hypertension`, which applies the clinical ACC/AHA
    rule instead of a data-driven split.
    """
    threshold = float(np.median(y)) if threshold is None else float(threshold)
    return (y > threshold).astype(int), threshold


def hypertension(ds):
    """Part 2 label: ACC/AHA stage-1 hypertension from measured blood pressure.

    Applies the clinical rule ``SBP >= 130 OR DBP >= 80`` to the dataset's
    systolic target (``ds['y']``) and reserved diastolic column (``ds['dbp']``).
    Because both blood-pressure columns are excluded from ``ds['X']``, predicting
    this label from the features alone is leakage-safe -- the Part 2 framing.

    Returns
    -------
    (labels, rule_str) : (ndarray of {0, 1}, str)
        labels[i] == 1 iff patient i meets the hypertension rule; rule_str names
        the rule for plots/reports.
    """
    if ds.get("dbp") is None:
        raise ValueError(
            "hypertension() needs a 'dbp' (diastolic BP) column, which the loaded "
            "dataset does not provide. The deployed NHANES dataset includes it; "
            "the synthetic reference fallback does not. Use binarize(ds['y']) for "
            "a generic split on systolic BP instead."
        )
    sbp = np.asarray(ds["y"], dtype=float)
    dbp = np.asarray(ds["dbp"], dtype=float)
    labels = ((sbp >= 130) | (dbp >= 80)).astype(int)
    rule_str = "SBP>=130 OR DBP>=80 (ACC/AHA stage-1 hypertension)"
    return labels, rule_str
