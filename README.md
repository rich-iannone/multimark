<p align="center">
<a href="https://pypi.org/project/multimark/"><img src="https://img.shields.io/pypi/v/multimark?logo=python&logoColor=white&color=orange" alt="PyPI"></a>
<a href="https://pypi.org/project/multimark/"><img src="https://img.shields.io/pypi/pyversions/multimark.svg" alt="Python versions"></a>
<a href="https://pypistats.org/packages/multimark"><img src="https://img.shields.io/pypi/dm/multimark" alt="Downloads"></a>
<a href="https://choosealicense.com/licenses/mit/"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
<a href="https://github.com/rich-iannone/multimark/actions/workflows/ci.yml"><img src="https://github.com/rich-iannone/multimark/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
</p>

# multimark

Python bindings to [cmark-gfm](https://github.com/github/cmark-gfm), the C reference implementation of [CommonMark](https://commonmark.org/) with GitHub Flavored Markdown extensions.

Renders Markdown to **HTML**, **LaTeX**, **groff man**, **XML**, and **normalized CommonMark**: all from a single, lightweight package.

## Installation

```bash
pip install multimark
```

Wheels are available for Linux, macOS, and Windows (Python 3.9+). No system dependencies required.

## Quick Start

```python
from multimark import markdown_to_html, markdown_to_latex

html = markdown_to_html("**Hello**, *world*!")
# '<p><strong>Hello</strong>, <em>world</em>!</p>\n'

latex = markdown_to_latex("**Hello**, *world*!")
# '\\textbf{Hello}, \\emph{world}!\n'
```

## Renderers

| Function | Output Format |
|----------|---------------|
| `markdown_to_html()` | HTML |
| `markdown_to_latex()` | LaTeX |
| `markdown_to_man()` | groff man page |
| `markdown_to_commonmark()` | Normalized CommonMark |
| `markdown_to_xml()` | XML (AST representation) |

## Options

Use named boolean keyword arguments for common settings:

```python
from multimark import markdown_to_html, markdown_to_latex

# Smart punctuation (curly quotes, em-dashes)
markdown_to_html('"Hello" -- world...', smart=True)
# '<p>\u201cHello\u201d \u2013 world\u2026</p>\n'

# Allow raw HTML passthrough (safe mode is the default)
markdown_to_html('<div>hi</div>', unsafe=True)
# '<div>hi</div>\n'

# Source position attributes
markdown_to_html('**Hello**', sourcepos=True)
# '<p data-sourcepos="1:1-1:9"><strong>Hello</strong></p>\n'

# Line wrapping (LaTeX, man, and commonmark renderers)
markdown_to_latex('**Hello**, *world*!', width=80)
# '\\textbf{Hello}, \\emph{world}!\n'

# Footnotes
markdown_to_html('Text[^1]\n\n[^1]: A footnote\n', footnotes=True)
# '<p>Text<sup class="footnote-ref">...</sup></p>\n<section class="footnotes">...\n'
```

Or compose flags with the `Options` bitmask:

```python
from multimark import markdown_to_html, Options

html = markdown_to_html(text, options=Options.SMART | Options.UNSAFE)
```

## GFM Extensions

Enable GitHub Flavored Markdown extensions by name:

```python
from multimark import markdown_to_html

# Tables
markdown_to_html('| A | B |\n|---|---|\n| 1 | 2 |\n', extensions=["table"])
# '<table>\n<thead>\n<tr>\n<th>A</th>\n<th>B</th>\n</tr>...\n'

# Strikethrough
markdown_to_html('~~deleted~~', extensions=["strikethrough"])
# '<p><del>deleted</del></p>\n'

# Multiple extensions
html = markdown_to_html(text, extensions=["table", "strikethrough", "autolink", "tasklist", "tagfilter"])
```

Available extensions: `table`, `strikethrough`, `autolink`, `tagfilter`, `tasklist`.

## All Renderer Parameters

Every renderer accepts:

- **`text`** — Markdown string
- **`options`** — Raw bitmask (default `0`)
- **`extensions`** — List of GFM extension names (default `()`)
- **`smart`** — Smart punctuation
- **`hardbreaks`** — Render soft breaks as `<br>`
- **`unsafe`** — Allow raw HTML
- **`normalize`** — Consolidate adjacent text nodes
- **`footnotes`** — Enable footnote syntax

Additional parameters:

- **`sourcepos`** — Source position attributes (HTML and XML only)
- **`width`** — Line wrap column (LaTeX, man, and commonmark only; `0` = no wrap)

## License

MIT (Python wrapper) and BSD-2-Clause (vendored cmark-gfm).