"""Build the deployed clinical dataset from NHANES 2021-2022 (cycle suffix ``_L``).

This is a BUILD-time ETL script, run by the instructor, not by students. It
downloads six public NHANES XPT files, merges them on the respondent id
``SEQN``, derives systolic / diastolic blood pressure from the oscillometric
readings, applies an adult complete-case filter, and writes
``data/nhanes_2021_2022.csv`` -- the dataset that ``info521.data.load_clinical``
loads by default.

The student-facing loader stays numpy-only; pandas is used *here only* to parse
the SAS XPORT files and assemble the CSV.

NHANES 2021-2022 was the first post-pandemic field cycle, with some sampling
adjustments relative to the pre-2020 cycles. We deliberately IGNORE the NHANES
survey weights: this is an algorithms course about estimators, not about
population inference, so we treat the retained respondents as a plain i.i.d.
sample. (If you ever need population estimates, weight by ``WTMECPRP`` from
DEMO_L instead.)

Blood pressure note: auscultatory BP (the old ``BPX`` file, variables
``BPXSY*`` / ``BPXDI*``) was discontinued after the 2017-2018 cycle. NHANES
2021-2022 ships OSCILLOMETRIC blood pressure only, in ``BPXO_L``, with reading
variables ``BPXOSY1..3`` (systolic) and ``BPXODI1..3`` (diastolic) -- different
names from the auscultatory file, verified against the CDC codebook
(https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BPXO_L.htm).

Run:  python data/build_nhanes.py
      (downloads are cached in data/raw/; delete that folder to force a refetch)
"""

from __future__ import annotations

import os
import sys
import urllib.request

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Paths and remote layout
# --------------------------------------------------------------------------- #
_HERE = os.path.dirname(os.path.abspath(__file__))
_RAW_DIR = os.path.join(_HERE, "raw")
_OUT_CSV = os.path.join(_HERE, "nhanes_2021_2022.csv")

# Primary CDC location for the 2021-2022 (suffix _L) public data files. Both this
# path and the legacy .../Nhanes/2021-2022/ path currently resolve; we try this
# one first and fall back if a file 404s.
_BASE_URLS = [
    "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles",
    "https://wwwn.cdc.gov/Nchs/Nhanes/2021-2022",
]

# The six source files for the 2021-2022 cycle.
_FILES = {
    "DEMO": "DEMO_L.xpt",    # demographics  -> RIDAGEYR
    "BPXO": "BPXO_L.xpt",    # blood pressure, oscillometric -> BPXOSY1..3 / BPXODI1..3
    "BMX": "BMX_L.xpt",      # body measures -> BMXBMI, BMXWAIST
    "TCHOL": "TCHOL_L.xpt",  # total cholesterol -> LBXTC
    "HDL": "HDL_L.xpt",      # HDL cholesterol   -> LBDHDD
    "GHB": "GHB_L.xpt",      # glycohemoglobin   -> LBXGH
}

# Oscillometric BP reading columns (verified against the BPXO_L codebook).
_SBP_READINGS = ["BPXOSY1", "BPXOSY2", "BPXOSY3"]
_DBP_READINGS = ["BPXODI1", "BPXODI2", "BPXODI3"]

# Final output column order: features first, then the continuous target (sbp),
# then dbp (reserved for the Part 2 hypertension label only).
_OUT_COLUMNS = ["age", "bmi", "waist", "chol", "hdl", "hba1c", "sbp", "dbp"]


# --------------------------------------------------------------------------- #
# Download + cache
# --------------------------------------------------------------------------- #
def _download(filename: str) -> str:
    """Fetch ``filename`` into data/raw/, caching it. Returns the local path."""
    os.makedirs(_RAW_DIR, exist_ok=True)
    dest = os.path.join(_RAW_DIR, filename)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"  cached  {filename}")
        return dest

    last_err: Exception | None = None
    for base in _BASE_URLS:
        url = f"{base}/{filename}"
        try:
            print(f"  fetch   {filename}  <-  {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "info521-build/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            with open(dest, "wb") as fh:
                fh.write(data)
            return dest
        except Exception as exc:  # noqa: BLE001 - report and try the next mirror
            last_err = exc
            print(f"          failed ({exc}); trying next mirror")
    raise RuntimeError(f"could not download {filename}: {last_err}")


def _read_xpt(filename: str, keep: list[str]) -> pd.DataFrame:
    """Download (if needed) and read an XPT file, keeping ``keep`` columns."""
    path = _download(filename)
    df = pd.read_sas(path, format="xport")
    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise KeyError(
            f"{filename}: expected columns {missing} not found. "
            f"Available: {sorted(df.columns)}"
        )
    return df[keep].copy()


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build() -> pd.DataFrame:
    print("Reading NHANES 2021-2022 source files (suffix _L):")

    demo = _read_xpt(_FILES["DEMO"], ["SEQN", "RIDAGEYR"])
    bpxo = _read_xpt(_FILES["BPXO"], ["SEQN", *_SBP_READINGS, *_DBP_READINGS])
    bmx = _read_xpt(_FILES["BMX"], ["SEQN", "BMXBMI", "BMXWAIST"])
    tchol = _read_xpt(_FILES["TCHOL"], ["SEQN", "LBXTC"])
    hdl = _read_xpt(_FILES["HDL"], ["SEQN", "LBDHDD"])
    ghb = _read_xpt(_FILES["GHB"], ["SEQN", "LBXGH"])

    # --- derive oscillometric SBP / DBP -----------------------------------
    # NHANES codes an unusable reading as 0 (or leaves it missing); ignore both
    # and average the readings that remain. ``.where(x != 0)`` turns any 0 into
    # NaN, so by construction no reading equal to 0 is ever "used" in the mean
    # (this satisfies the "drop rows where any BP reading used is 0" rule). A row
    # with no usable systolic *or* diastolic reading becomes NaN here and is
    # dropped by the complete-case filter below.
    sy = bpxo[_SBP_READINGS].where(bpxo[_SBP_READINGS] != 0)
    di = bpxo[_DBP_READINGS].where(bpxo[_DBP_READINGS] != 0)
    bp = pd.DataFrame({
        "SEQN": bpxo["SEQN"],
        "sbp": sy.mean(axis=1, skipna=True),
        "dbp": di.mean(axis=1, skipna=True),
    })

    # --- inner-join everything on SEQN ------------------------------------
    df = (
        demo
        .merge(bp, on="SEQN", how="inner")
        .merge(bmx, on="SEQN", how="inner")
        .merge(tchol, on="SEQN", how="inner")
        .merge(hdl, on="SEQN", how="inner")
        .merge(ghb, on="SEQN", how="inner")
    )

    # --- rename to the course's column contract ---------------------------
    df = df.rename(columns={
        "RIDAGEYR": "age",
        "BMXBMI": "bmi",
        "BMXWAIST": "waist",
        "LBXTC": "chol",
        "LBDHDD": "hdl",
        "LBXGH": "hba1c",
    })

    n_merged = len(df)

    # --- inclusion: adults 18..79 (avoid the age-80 topcode) --------------
    df = df[(df["age"] >= 18) & (df["age"] <= 79)]
    n_adults = len(df)

    # --- complete cases on every output column ----------------------------
    df = df[_OUT_COLUMNS].dropna()
    n_complete = len(df)

    print(
        f"\nMerged rows: {n_merged}  ->  adults 18-79: {n_adults}  ->  "
        f"complete cases: {n_complete}"
    )

    return df.reset_index(drop=True)


# --------------------------------------------------------------------------- #
# QA summary
# --------------------------------------------------------------------------- #
def qa_summary(df: pd.DataFrame) -> None:
    print("\n" + "=" * 70)
    print("QA SUMMARY  --  NHANES 2021-2022 deployed dataset")
    print("=" * 70)

    n = len(df)
    sbp = df["sbp"].to_numpy()
    dbp = df["dbp"].to_numpy()

    print(f"N retained                 : {n}")
    print(f"age range                  : {df['age'].min():.0f} - {df['age'].max():.0f} yr")
    print(f"sbp mean (SD)              : {sbp.mean():.2f} ({sbp.std(ddof=1):.2f}) mmHg")
    print(f"dbp mean (SD)              : {dbp.mean():.2f} ({dbp.std(ddof=1):.2f}) mmHg")

    # ACC/AHA stage-1 hypertension by measured BP: SBP>=130 OR DBP>=80.
    htn = (sbp >= 130) | (dbp >= 80)
    print(f"hypertension prevalence    : {htn.mean():.3f}   (rule: SBP>=130 OR DBP>=80)")

    print("\nper-column missingness (should all be 0 post-filter):")
    miss = df[_OUT_COLUMNS].isna().sum()
    for col in _OUT_COLUMNS:
        print(f"  {col:<6}: {int(miss[col])}")

    print("\n8x8 correlation matrix:")
    corr = df[_OUT_COLUMNS].corr()
    with pd.option_context("display.float_format", lambda v: f"{v:6.3f}"):
        print(corr.to_string())
    print("=" * 70)


def main() -> int:
    df = build()
    df.to_csv(_OUT_CSV, index=False, float_format="%.4f")
    print(f"\nWrote {_OUT_CSV}: {df.shape[0]} rows x {df.shape[1]} cols")
    print(f"  column order: {', '.join(_OUT_COLUMNS)}")
    qa_summary(df)
    return 0


if __name__ == "__main__":
    sys.exit(main())
