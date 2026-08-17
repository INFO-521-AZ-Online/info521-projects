#!/usr/bin/env python3
"""Build the grading specs reference (PDF + DOCX) from GRADING.md.

GRADING.md is the source of truth for the specs-grading mechanics. This renders
it as a shareable course document in the house style: the UA banner, the
course-schedule placement band, hub-rewritten links, both formats.

    python tools/build_grading.py

Requires: quarto (bundles Typst), pdftotext (Poppler), pandoc.
"""
import re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _uastyle import frontmatter, banner, placement, rewrite_links

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pdfs"
SCRATCH = Path(__file__).resolve().parent

SUBTITLE = "INFO 521 · Machine Learning Foundations · specs grading reference"

HOWTO = (
    "This is the reference for how project work is graded: specifications, not points. "
    "It governs the mechanics; the category weights live in the syllabus. Milestone "
    "notebooks carry their own Satisfactory criteria, and the checkpoint quizzes run "
    "on D2L."
)

BAND = ("Reference document. Applies to every project milestone and checkpoint quiz "
        "across both projects; no single week.")


def main():
    OUT.mkdir(exist_ok=True)
    md = (ROOT / "GRADING.md").read_text(encoding="utf-8")
    lines = md.split("\n")
    title = lines[0].lstrip("# ").strip()
    body = rewrite_links("\n".join(lines[1:]).strip())

    doc = (frontmatter(title, SUBTITLE)
           + banner("How to read this", HOWTO)
           + placement(BAND)
           + "\n" + body + "\n")

    print("Building grading specs reference:")
    built = []
    for fmt, ext in (("typst", "pdf"), ("docx", "docx")):
        qmd = SCRATCH / "_grading-specs.qmd"
        qmd.write_text(doc, encoding="utf-8")
        r = subprocess.run(["quarto", "render", str(qmd), "--to", fmt],
                           capture_output=True, text=True, cwd=SCRATCH)
        produced = SCRATCH / f"_grading-specs.{ext}"
        qmd.unlink(missing_ok=True)
        if r.returncode != 0 or not produced.exists():
            print(f"  FAIL grading-specs.{ext}\n{r.stdout[-1200:]}{r.stderr[-1200:]}")
            sys.exit(1)
        dest = OUT / f"grading-specs.{ext}"
        shutil.move(str(produced), str(dest))
        built.append(dest)
        print(f"  {dest.relative_to(ROOT)}")

    print("\nChecks:")
    bad = 0
    for p in built:
        if p.suffix == ".pdf":
            txt = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
        else:
            txt = subprocess.run(["pandoc", "-t", "plain", str(p)], capture_output=True, text=True).stdout
        # both extractors wrap lines mid-phrase; match on normalized whitespace
        txt = re.sub(r"\s+", " ", txt)
        problems = []
        for term in ("closed-book", "in-class", "retake", "can derive unaided",
                     "final replaces lowest midterm passed", "Checkpoint 4", "Checkpoint 5"):
            if term in txt:
                problems.append(f"stale term {term!r}")
        for need in ("D2L quizzes", "gates the milestone due", "Course-schedule placement",
                     "How to read this", "Checkpoint quizzes 1.1 to 1.3"):
            if need not in txt:
                problems.append(f"missing {need!r}")
        if "#block(" in txt:
            problems.append("raw typst leaked")
        if problems:
            print(f"  FAIL  {p.name}: {'; '.join(problems)}")
            bad += 1
        else:
            print(f"  clean {p.name}")
    if bad:
        sys.exit(1)
    print("\nBoth grading-specs artifacts built and checked.")


if __name__ == "__main__":
    main()
