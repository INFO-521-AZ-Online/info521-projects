# Course-document PDFs and DOCX

UA-styled PDFs (Typst, same look as the hub syllabus) of the project overviews and
milestone briefs, for D2L, each with a matching **DOCX** (hub `reference.docx` styles) as
the editable copy. Every artifact carries a **Course-schedule placement** band mapping it
to the week/module arc.

**Checkpoint quiz artifacts are not here.** They carry answers and this repo is public, so
the whole quiz pipeline lives in the private homeworks repo at
`info521-homeworks-2026/quizzes/` (built into `quizzes/out/`).

Everything here is generated. Do not hand-edit an artifact; edit its source and rebuild.

## Regenerating

```bash
python tools/build_overviews.py      # 2 project-overview PDFs
python tools/build_milestones.py     # 9 milestone assignment briefs
```

The quizzes build separately, from the private repo:
`python quizzes/build_quizzes.py` in `info521-homeworks-2026`.

Both resolve paths from the repo root, so they work from any working directory. All
require `quarto` (which bundles Typst) and `pdftotext` (Poppler). Shared UA styling lives
in `tools/_uastyle.py`, so the builders cannot drift apart, and it also pins
`mainfont: Arial` so every course PDF matches the syllabus font stack.

| Artifact | Built from |
|---|---|
| `grading-specs.{pdf,docx}` | `GRADING.md` |
| `overview-project-1.{pdf,docx}` | `project-1/README.md` |
| `overview-project-2.{pdf,docx}` | `project-2/README.md` |
| `milestone-*.{pdf,docx,html}` | the milestone notebooks themselves (`project-1/*.qmd`, `project-2/*.qmd`) |

## Naming scheme

Every D2L artifact is `<kind>-<course-position>-<suffix>`, prefix first, so the families
group and sort correctly in a file listing:

```
overview-project-1.pdf
milestone-1.1-least-squares.pdf
```

A checkpoint is named for the milestone it gates, so **quiz 2.1 gates milestone 2.1** and
**quiz 2.3 gates milestone 2.3**. Each quiz is due the week before its milestone. The quiz
artifacts themselves are built in the private repo; see
`info521-homeworks-2026/quizzes/README.md`.

The retired checkpoint-notebook PDFs live in `../_to_delete/notebook-model/` until
deleted.

## D2L upload map

| Upload | As |
|---|---|
| `grading-specs.pdf` | content topic under Course Admin / grading (DOCX is the editable copy) |
| `overview-project-*.pdf` | content topic introducing each project |
| `milestone-*.pdf` | the assignment brief attached to each milestone's D2L assignment |
| `milestone-*.html` | the same brief as a D2L **content topic**: upload the file (do not paste into the WYSIWYG editor). Fully self-contained: math is pre-rendered MathML, no scripts, no CDN |

Quiz imports come from `info521-homeworks-2026/quizzes/out/`.
