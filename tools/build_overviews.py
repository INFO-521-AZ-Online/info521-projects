#!/usr/bin/env python3
"""Build the project overviews (PDF + DOCX) from the project READMEs.

Source of truth is project-1/README.md and project-2/README.md. This script adds
the UA banner and the course-schedule placement band, rewrites repo-relative
links to hub URLs (they are correct on GitHub but dead in a PDF on D2L), and
renders through Quarto's Typst format.

    python tools/build_overviews.py

Requires: quarto (bundles Typst), pdftotext (Poppler).
"""
import shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _uastyle import frontmatter, banner, placement, rewrite_links

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pdfs"
SCRATCH = Path(__file__).resolve().parent

SUBTITLE = "INFO 521 · Machine Learning Foundations · project overview"

SPEC = {
    "project-1": dict(
        src="project-1/README.md",
        out="overview-project-1",
        placement=(
            "Part 1 of the project: assigned Week 1, due Week 5, the "
            "midpoint. Milestones on the module arc: 1.1 Least Squares (M1 to M2, due Wk 3), "
            "then 1.2 Maximum Likelihood (M3, due Wk 4), then 1.3 Bayesian (M4, due Wk 5; the "
            "conjugate Gaussian posterior is the Part 1 endpoint), then 1.4 Synthesis (due "
            "Wk 5). Gating: Checkpoint quizzes 1.1 to 1.3, each due the week before the "
            "milestone it gates."
        ),
    ),
    "project-2": dict(
        src="project-2/README.md",
        out="overview-project-2",
        placement=(
            "Part 2 of the project: begins at the midpoint (Week 5), due "
            "Week 7.5. Milestones on the module arc: 2.1 Approximate inference (M5, due Wk 6), "
            "then 2.2 Classification and SVM (M6, due Wk 6), then 2.3 Clustering (M6, due "
            "Wk 7), then 2.4 PCA (M7, due Wk 7), then 2.5 Synthesis (due Wk 7.5). Gating: "
            "Checkpoint quiz 2.1 (Gate A, Wk 5), quiz 2.3 (Gate B, Wk 6)."
        ),
    ),
}

HOWTO = (
    "This overview is the project brief. The milestone notebooks carry the authoritative "
    "Satisfactory criteria, each stated at the top of its own notebook. Grading mechanics, "
    "including the gate and bundle structure, are on the course Assessment page."
)


def build(key: str, s: dict):
    md = (ROOT / s["src"]).read_text(encoding="utf-8")
    lines = md.split("\n")
    title = lines[0].lstrip("# ").strip()
    body = rewrite_links("\n".join(lines[1:]).strip())

    doc = (frontmatter(title, SUBTITLE)
           + banner("How to read this", HOWTO)
           + placement(s["placement"])
           + "\n" + body + "\n")

    made = []
    for fmt, ext in (("typst", "pdf"), ("docx", "docx")):
        qmd = SCRATCH / f"_{key}-overview.qmd"
        qmd.write_text(doc, encoding="utf-8")
        r = subprocess.run(["quarto", "render", str(qmd), "--to", fmt],
                           capture_output=True, text=True, cwd=SCRATCH)
        produced = SCRATCH / f"_{key}-overview.{ext}"
        qmd.unlink(missing_ok=True)
        if r.returncode != 0 or not produced.exists():
            print(f"  FAIL {s['out']}.{ext}\n{r.stdout[-1200:]}{r.stderr[-1200:]}")
            return None
        dest = OUT / f"{s['out']}.{ext}"
        shutil.move(str(produced), str(dest))
        made.append(dest)
    return made


def main():
    OUT.mkdir(exist_ok=True)
    print("Building project overviews:")
    built = []
    for key, s in SPEC.items():
        made = build(key, s)
        if made:
            built.extend(made)
            for d in made:
                print(f"  {d.relative_to(ROOT)}")

    if len(built) != 2 * len(SPEC):
        sys.exit(1)

    print("\nChecks:")
    bad = 0
    for p in built:
        if p.suffix == ".pdf":
            txt = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
        else:
            txt = subprocess.run(["pandoc", "-t", "plain", str(p)], capture_output=True, text=True).stdout
        problems = []
        # no dead repo-relative links survived the rewrite
        if "../GRADING.md" in txt or "../checkpoints/" in txt:
            problems.append("repo-relative link survived")
        # no stale checkpoint vocabulary
        for term in ("closed-book", "in-class", "the slips"):
            if term in txt:
                problems.append(f"stale term {term!r}")
        # the placement band rendered rather than leaking raw Typst
        if "Course-schedule placement" not in txt or "#block(" in txt:
            problems.append("placement band did not render")
        if "Assigned Week 1, due Week 4" in txt or "Assigned Week 5, due Week 7." in txt.replace("due Week 7.5", "") or "second project slot" in txt:
            problems.append("stale project due-week in the placement band")
        if problems:
            print(f"  FAIL  {p.name}: {'; '.join(problems)}")
            bad += 1
        else:
            print(f"  clean {p.name}")

    if bad:
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
