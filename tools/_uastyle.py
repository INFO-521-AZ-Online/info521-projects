"""Shared UA styling for the course-document PDFs.

Both PDF builders (checkpoints, project overviews) render through Quarto's Typst
format. The banner blocks live here so the two builders cannot drift apart.
"""
import re

UA_NAVY = "#1B4F72"
UA_RED = "#AB0520"
HUB = "https://gchism94.github.io/info521"

# Repo-relative links are correct on GitHub but dead in a PDF on D2L.
# Rewrite them to hub URLs at render time; the source files stay correct as-is.
LINK_REWRITES = [
    (r'`\.\./GRADING\.md`', f'the [Assessment page]({HUB}/assessment.html)'),
    (r'`\.\./checkpoints/`', f'[the checkpoint quizzes]({HUB}/assessment.html#checkpoints)'),
    (r'`\.\./([A-Za-z0-9_.-]+)\.md`', rf'the [\1]({HUB}/assessment.html)'),
]


def rewrite_links(md: str) -> str:
    for pat, sub in LINK_REWRITES:
        md = re.sub(pat, sub, md)
    return md


def frontmatter(title: str, subtitle: str) -> str:
    return f"""---
title: "{title}"
subtitle: "{subtitle}"
format:
  typst:
    papersize: us-letter
    margin:
      x: 1.1in
      y: 1in
    fontsize: 10.5pt
    section-numbering: ""
    # Matches the syllabus font stack. Arial is the resolvable member of
    # ("Helvetica Neue", "Helvetica", "Arial") across macOS and Linux, and
    # Quarto's typst template only honours the `mainfont` knob here.
    mainfont: Arial
  docx:
    # Vendored copy of the hub repo's reference.docx, so the DOCX outputs match
    # the hub handouts. Renders happen from tools/, hence the bare filename.
    reference-doc: reference.docx
  html:
    # One portable file for D2L: everything inlined, and math pre-rendered to
    # MathML at build time so the file needs NO scripts and NO network (the
    # default MathJax route loads from a CDN at view time, which a locked-down
    # D2L instance can block). Upload as a content-topic FILE.
    embed-resources: true
    html-math-method: mathml
    toc: true
# These render as standalone D2L files, so cross-format download links would
# point at siblings that are not uploaded next to them.
format-links: false
---
"""


def banner(heading: str, body: str, accent: str = UA_NAVY, tint: str = "#f2f6f9") -> str:
    """The tinted callout at the top of each document.

    Raw Typst renders only in the PDF; DOCX output silently drops it. Both
    formats therefore get their own copy behind when-format guards.
    """
    return f"""
::: {{.content-visible when-format="typst"}}
```{{=typst}}
#block(
  fill: rgb("{tint}"),
  stroke: (left: 3pt + rgb("{accent}")),
  inset: 10pt,
  radius: 2pt,
  width: 100%,
)[
  #text(weight: "bold", fill: rgb("{UA_NAVY}"))[{heading}]
  #linebreak()
  {body}
]

#v(6pt)
```
:::

::: {{.content-visible when-format="docx"}}
**{heading}.** {body}
:::

::: {{.content-visible when-format="html"}}
::: {{.callout-note appearance="simple"}}
## {heading}
{body}
:::
:::
"""


def placement(body: str) -> str:
    """The grey Course-schedule placement band. Same dual-format treatment."""
    return f"""
::: {{.content-visible when-format="typst"}}
```{{=typst}}
#block(
  fill: rgb("#eef2f6"),
  inset: 8pt,
  radius: 2pt,
  width: 100%,
)[
  #text(weight: "bold", fill: rgb("{UA_NAVY}"))[Course-schedule placement.]
  {body}
]

#v(6pt)
```
:::

::: {{.content-visible when-format="docx"}}
**Course-schedule placement.** {body}
:::

::: {{.content-visible when-format="html"}}
::: {{.callout-tip appearance="simple"}}
## Course-schedule placement
{body}
:::
:::
"""
