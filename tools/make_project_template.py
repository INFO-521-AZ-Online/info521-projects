#!/usr/bin/env python3
"""Stamp this repo into a Classroom 50 template repo for the projects.

The homework repo has `scripts/make_template_repo.sh` per unit. This is the
projects counterpart, and it exists because the projects had no distribution
pipeline at all: students were never told how to obtain or submit 55% of their
grade.

Local only. It does NOT create remotes or push; that is the instructor's step
and the commands are printed at the end.

    python tools/make_project_template.py

What ships is an explicit ALLOWLIST, not a glob-minus-exclusions, so adding a
file to the repo cannot silently add it to the student template. The build then
re-verifies that nothing carrying an answer key made it in.

Requires: git.
"""
import re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "projects-template"

# Explicit allowlist. Directories ship recursively with the filters noted.
# The repo README is instructor-facing and is NOT shipped; the template gets the
# student README written below instead.
SHIP_FILES = [
    "GRADING.md",
    "pyproject.toml",
    "environment.yml",
    ".gitignore",
]

STUDENT_README = """\
# INFO 521: The Project

This is your personal repository for the INFO 521 course project: one clinical
dataset, two parts, nine milestone notebooks. Part 1 (One Problem, Three Lenses)
is due at the Week 5 midpoint; Part 2 (From Inference to Discovery) closes the
term at Week 7.5. It is private to you and the teaching team.

## What is here

```
project-1/         milestones 1.1 to 1.4 (least squares, MLE, Bayesian, synthesis)
project-2/         milestones 2.1 to 2.5 (approximate inference, SVM, k-means, PCA, synthesis)
common/info521/    the course plumbing library: data loader, plotting, self-checks.
                   It contains no fitting routines; every estimator is yours to build.
data/              the NHANES 2021-2022 extract and the synthetic fallback
GRADING.md         how milestones are judged: Satisfactory criteria, gates, revise cycle
```

Each milestone notebook lists its Satisfactory criteria at the top; the milestone
briefs, checkpoint quizzes, and due dates live on D2L.

## Getting started

Python 3.11 (not 3.14; the pinned numpy has no 3.14 support).

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e .
quarto render project-1/1.1-least-squares.qmd
```

## Ground rules

Implement every estimator from scratch in NumPy/SciPy: no scikit-learn, no
off-the-shelf solver, sampler, or metric function. From scratch rules out
libraries, never your own prior work: code you built and certified in a homework
unit may be copied or imported into any milestone, and reusing it is encouraged.
See GRADING.md, "From scratch, defined."

## Submitting

Commit and push to this repository. Each push is a submission; work is graded
against the Satisfactory criteria after the milestone's due date, with one
revise-and-resubmit cycle per milestone.
"""
SHIP_GLOBS = [
    ("project-1", "*.qmd"),
    ("project-1", "README.md"),
    ("project-2", "*.qmd"),
    ("project-2", "README.md"),
    ("common/info521", "*.py"),
    ("data", "*.csv"),
    ("data", "README.md"),
    ("data", "build_nhanes.py"),
    ("data", "generate_reference_data.py"),
]

# Nothing matching these may appear in the built template.
FORBIDDEN = [
    re.compile(r"^checkpoints/"),   # quiz sources and keys; checkpoints are D2L quizzes now
    re.compile(r"^pdfs/"),                                # D2L artifacts, not repo content
    re.compile(r"^tools/"),                               # instructor build scripts
    re.compile(r"^build/"),
    re.compile(r"AUDIT_PROJECTS\.md$"),
    re.compile(r"CLAUDE_CODE_HANDOFF\.md$"),
    re.compile(r"INSTRUCTOR"),
    re.compile(r"_to_delete/"),
    re.compile(r"data/raw/"),                             # large XPT build inputs
]

# Strings that must not appear in any shipped text file. The heading form only,
# because audit and handoff docs legitimately discuss the key-release policy in
# prose and flagging the bare phrase would fail the build on documentation.
KEY_MARKERS = ["## Answer key", "_reference.py"]


def collect():
    picked = []
    for f in SHIP_FILES:
        p = ROOT / f
        if p.exists():
            picked.append(p)
    for d, pat in SHIP_GLOBS:
        for p in sorted((ROOT / d).glob(pat)):
            if p.is_file():
                picked.append(p)
    return picked


def main():
    picked = collect()
    if not picked:
        print("nothing collected; run from a checkout with the project files present")
        sys.exit(1)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    print("Assembling student template:")
    for src in picked:
        rel = src.relative_to(ROOT)
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    (OUT / "README.md").write_text(STUDENT_README, encoding="utf-8")
    print(f"  {len(picked)} files + student README -> {OUT.relative_to(ROOT)}")

    # --- verification -------------------------------------------------------
    print("\nChecks:")
    bad = 0

    shipped = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    hits = [s for s in shipped for pat in FORBIDDEN if pat.search(s)]
    if hits:
        print(f"  FAIL  forbidden paths shipped: {hits[:4]}")
        bad += 1
    else:
        print(f"  clean no forbidden path shipped ({len(shipped)} files)")

    leaked = []
    for p in OUT.rglob("*"):
        if not p.is_file() or p.suffix not in {".qmd", ".md", ".py", ".yml", ".toml"}:
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for m in KEY_MARKERS:
            if m in t:
                leaked.append((p.relative_to(OUT).as_posix(), m))
    if leaked:
        print(f"  FAIL  answer-key marker in shipped file: {leaked[:3]}")
        bad += 1
    else:
        print("  clean no answer-key marker in any shipped file")

    # the nine milestone notebooks must actually be there; checkpoints must NOT
    # (they are D2L quizzes, not repo content, since the 2026-08-03 merge)
    n_cp = len(list((OUT / "checkpoints").glob("*"))) if (OUT / "checkpoints").exists() else 0
    n_ms = (len(list((OUT / "project-1").glob("*.qmd"))) +
            len(list((OUT / "project-2").glob("*.qmd"))))
    if n_cp != 0 or n_ms != 9:
        print(f"  FAIL  expected 0 checkpoint files and 9 milestones, got {n_cp} and {n_ms}")
        bad += 1
    else:
        print("  clean 9 milestone notebooks; no checkpoint files (quizzes live on D2L)")

    if bad:
        sys.exit(1)

    subprocess.run(["git", "init", "-q"], cwd=OUT, check=True)
    subprocess.run(["git", "add", "-A"], cwd=OUT, check=True)
    subprocess.run(["git", "-c", "user.name=course-build",
                    "-c", "user.email=course-build@local",
                    "commit", "-qm", "Projects template repo (generated)"],
                   cwd=OUT, check=True)

    print(f"""
Done: {OUT}  (fresh git repo, student-facing)

Next (your steps):
  gh repo create INFO-521-AZ-Online/info521-projects-template --public \\
      --source={OUT} --remote=origin --push
  gh repo edit INFO-521-AZ-Online/info521-projects-template --template   # Classroom50 requires is_template
  gh teacher assignment add INFO-521-AZ-Online info521 projects \\
      --name "Projects" --template INFO-521-AZ-Online/info521-projects-template

NOTE the -template suffix: INFO-521-AZ-Online/info521-projects is already the
pushed source repo. Do not target that name here, it is a different repo with
a different job (this one is the stripped Classroom 50 assignment template).

Make the template PUBLIC: with the org base permission at "No permission",
students can only read a public template (Classroom 50 wiki, Assignment
Templates). The builder ships nothing answer-bearing, so public is safe.
Checkpoints are D2L quizzes and never
ship in the repo; their question banks, keys and builder live in the private
repo at info521-homeworks-2026/quizzes/.""")


if __name__ == "__main__":
    main()
