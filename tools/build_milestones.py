#!/usr/bin/env python3
"""Build the D2L brief for each project milestone: PDF, DOCX, and portable HTML.

Source of truth is the milestone notebooks themselves (project-1/*.qmd,
project-2/*.qmd). This script strips the YAML front matter, turns executable
`{python}` cells into static listings (the PDF is a brief, it should not run
anything), adds the UA banner and the course-schedule placement band, rewrites
repo-relative links to hub URLs, and renders through Quarto's Typst format.

The scaffold is deliberately kept: the `# TODO:` comments inside the cells are
part of the assignment, not decoration, so a brief that dropped them would be
incomplete.

    python tools/build_milestones.py

Requires: quarto (bundles Typst), pdftotext (Poppler).
"""
import re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _uastyle import frontmatter, banner, placement, rewrite_links

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pdfs"
SCRATCH = Path(__file__).resolve().parent

SUBTITLE = "INFO 521 · Machine Learning Foundations · project milestone brief"

HOWTO = (
    "This is the assignment brief for one project milestone. The Satisfactory criteria below "
    "are authoritative: every one must be met, and it is all-or-nothing rather than partial "
    "credit. A Not-Yet returns with targeted feedback and one revise cycle. Do the work in the "
    "notebook distributed through Classroom 50; this PDF is the brief, not the workspace."
)

# (source, project, module span, due week, gate)
# The checkpoint quiz that gates a milestone is due the week BEFORE the
# milestone, so the derivation always lands first (schedule of 2026-08-03).
SPEC = [
    ("project-1/1.1-least-squares.qmd",            "Part 1", "M1 to M2", "due Week 3",   "Checkpoint quiz 1.1 (normal equations, Wk 2)"),
    ("project-1/1.2-maximum-likelihood.qmd",       "Part 1", "M3",       "due Week 4",   "Checkpoint quiz 1.2 (MLE for the weights, Wk 3)"),
    ("project-1/1.3-bayesian.qmd",                 "Part 1", "M4",       "due Week 5",   "Checkpoint quiz 1.3 (conjugate posterior, Wk 4)"),
    ("project-1/1.4-synthesis.qmd",                "Part 1", "M1 to M4", "due Week 5",   "structured peer review"),
    ("project-2/2.1-approximate-inference.qmd",    "Part 2", "M5",       "due Week 6",   "Checkpoint quiz 2.1 (Newton-Raphson update, Wk 5); Gate A"),
    ("project-2/2.2-classification.qmd",           "Part 2", "M6",       "due Week 6",   "Gate A, with 2.1 (Checkpoint quiz 2.1)"),
    ("project-2/2.3-clustering.qmd",               "Part 2", "M6",       "due Week 7",   "Checkpoint quiz 2.3 (k-means objective / PCA, Wk 6); Gate B"),
    ("project-2/2.4-dimensionality-reduction.qmd", "Part 2", "M7",       "due Week 7",   "Gate B, with 2.3 (Checkpoint quiz 2.3)"),
    ("project-2/2.5-synthesis.qmd",                "Part 2", "M5 to M7", "due Week 7.5", "structured peer review (synthesis)"),
]

DUE = {"Part 1": "Part 1 of the project: due Week 5, the midpoint",
       "Part 2": "Part 2 of the project: begins at the midpoint, due Week 7.5"}


def strip_frontmatter(md: str):
    """Return (title, subtitle, body) with the YAML block removed."""
    title = sub = ""
    if md.startswith("---"):
        end = md.index("\n---", 3)
        fm, body = md[3:end], md[end + 4:]
        for line in fm.split("\n"):
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("subtitle:"):
                sub = line.split(":", 1)[1].strip().strip('"')
    else:
        body = md
    return title, sub, body.strip()


def static_code(md: str) -> str:
    """Executable cells become static listings; the PDF must not run anything."""
    md = re.sub(r'^```\{python\}', '```python', md, flags=re.M)
    # drop cell-level execution options, which are noise in a printed brief
    md = re.sub(r'^#\|.*\n', '', md, flags=re.M)
    return md


def build(src, project, modules, week, gate):
    p = ROOT / src
    title, sub, body = strip_frontmatter(p.read_text(encoding="utf-8"))
    body = rewrite_links(static_code(body))

    band = (f"{DUE[project]}. This milestone covers {modules} and is {week}. "
            f"Gated by {gate}.")

    doc = (frontmatter(title, SUBTITLE if not sub else f"{SUBTITLE} · {sub}")
           + banner("How to read this", HOWTO)
           + placement(band)
           + "\n" + body + "\n")

    stem = "milestone-" + p.stem
    made = []
    for fmt, ext in (("typst", "pdf"), ("docx", "docx"), ("html", "html")):
        qmd = SCRATCH / f"_{stem}.qmd"
        qmd.write_text(doc, encoding="utf-8")
        r = subprocess.run(["quarto", "render", str(qmd), "--to", fmt],
                           capture_output=True, text=True, cwd=SCRATCH)
        produced = SCRATCH / f"_{stem}.{ext}"
        qmd.unlink(missing_ok=True)
        if r.returncode != 0 or not produced.exists():
            print(f"  FAIL {stem}.{ext}\n{r.stdout[-1200:]}{r.stderr[-1200:]}")
            return None
        dest = OUT / f"{stem}.{ext}"
        shutil.move(str(produced), str(dest))
        if ext == "html":
            # Quarto injects a cdnjs ES6-polyfill script ahead of MathJax; every
            # browser D2L supports has ES6, and it is the one external reference
            # in an otherwise self-contained file. Drop it.
            h = dest.read_text(encoding="utf-8")
            h2 = re.sub(r'\s*<script src="https://cdnjs\.cloudflare\.com/polyfill[^"]*"></script>', "", h)
            if h2 != h:
                dest.write_text(h2, encoding="utf-8")
        made.append(dest)
    return made


def main():
    OUT.mkdir(exist_ok=True)
    print("Building milestone briefs:")
    built = []
    for row in SPEC:
        made = build(*row)
        if made:
            built.extend(made)
            for d in made:
                print(f"  {d.relative_to(ROOT)}")

    if len(built) != 3 * len(SPEC):
        sys.exit(1)

    print("\nChecks:")
    bad = 0
    for p in built:
        if p.suffix == ".pdf":
            txt = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
        elif p.suffix == ".html":
            raw = p.read_text(encoding="utf-8")
            txt = re.sub(r"<script.*?</script>", "", raw, flags=re.S)
            txt = re.sub(r"<style.*?</style>", "", txt, flags=re.S)
            txt = re.sub(r"<[^>]+>", " ", txt)
            # a D2L-portable file must not depend on the network: catch both
            # literal src/href attributes AND runtime-injected script URLs
            # hiding inside JS strings (how MathJax's CDN loader slipped past
            # the first version of this check)
            if re.search(r'(?:src|href)="https?://', raw) or re.search(r'https?://cdn[^"\']*\.js', raw):
                txt += " EXTERNAL-DEPENDENCY-FOUND"
        else:
            txt = subprocess.run(["pandoc", "-t", "plain", str(p)], capture_output=True, text=True).stdout
        problems = []
        if "Satisfactory" not in txt:
            problems.append("no Satisfactory criteria")
        if "Course-schedule placement" not in txt or "#block(" in txt:
            problems.append("placement band did not render")
        if "How to read this" not in txt:
            problems.append("howto banner did not render")
        if "../GRADING.md" in txt or "../checkpoints/" in txt:
            problems.append("repo-relative link survived")
        for term in ("closed-book", "in-class", "passed in class"):
            if term in txt:
                problems.append(f"stale term {term!r}")
        # the scaffold must survive: these briefs are useless without the TODOs
        if "TODO" not in txt:
            problems.append("scaffold TODOs missing")
        if "EXTERNAL-DEPENDENCY-FOUND" in txt:
            problems.append("html not self-contained (external src/href)")
        if problems:
            print(f"  FAIL  {p.name}: {'; '.join(problems)}")
            bad += 1
        else:
            print(f"  clean {p.name}")

    if bad:
        sys.exit(1)
    print(f"\nAll {len(built)} milestone briefs built and checked.")


if __name__ == "__main__":
    main()
