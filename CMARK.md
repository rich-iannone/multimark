# cmark-python: Python Bindings for the cmark C Library

## Overview

A Python package providing bindings to the [cmark](https://github.com/commonmark/cmark) C reference implementation of CommonMark. This exposes **all** output renderers (HTML, LaTeX, groff man, CommonMark, XML) — filling the gap where existing Python packages (`cmarkgfm`) only expose HTML.

This is the Python equivalent of R's [`commonmark`](https://github.com/r-lib/commonmark) package.

## Motivation

- Python has no maintained, lightweight package for Markdown → LaTeX conversion
- `commonmark.py` (pure Python) is deprecated and only renders HTML
- `cmarkgfm` wraps the C library but only exposes `cmark_render_html()`
- `myst-parser` pulls in Sphinx + 50 transitive deps and requires Python ≥3.11
- `mistletoe` has an unresolved XSS vulnerability and no roundtripping support
- The C library already has LaTeX/man/XML/CommonMark renderers — they just need Python bindings

## Architecture

```
cmark-python/
├── src/
│   └── cmark_python/
│       ├── __init__.py          # Public API
│       ├── _cmark.py            # CFFI wrapper functions
│       ├── _build_cmark.py      # CFFI build script (compiles C)
│       └── cmark.cffi.h         # CFFI declarations for cmark.h
├── third_party/
│   └── cmark/                   # Vendored cmark C source (BSD-2)
├── tests/
│   ├── test_html.py
│   ├── test_latex.py
│   ├── test_man.py
│   ├── test_commonmark.py
│   ├── test_xml.py
│   └── test_extensions.py
├── pyproject.toml
├── setup.py                     # For CFFI C extension build
├── LICENSE                      # MIT (wrapper) + BSD-2 (cmark)
└── README.md
```

## Public API

```python
from cmark_python import (
    markdown_to_html,
    markdown_to_latex,
    markdown_to_man,
    markdown_to_commonmark,
    markdown_to_xml,
    parse_document,          # Returns opaque AST handle (Phase 3)
    render_html,             # Render a parsed AST
    render_latex,
    render_man,
    render_commonmark,
    render_xml,
    Options,                 # Enum/IntFlag for cmark options
)

# Simple usage
html = markdown_to_html("**bold** and *italic*")
latex = markdown_to_latex("**bold** and *italic*")
man = markdown_to_man("**bold** and *italic*")
xml = markdown_to_xml("**bold** and *italic*")
normalized = markdown_to_commonmark("**bold** and *italic*")

# With options
latex = markdown_to_latex(text, options=Options.SMART | Options.UNSAFE)

# With width (line wrapping for LaTeX/man/commonmark renderers)
latex = markdown_to_latex(text, width=80)

# GFM extensions (Phase 2)
html = markdown_to_html(text, extensions=["table", "strikethrough", "autolink"])
```

## C Functions to Bind

From `cmark.h` (upstream cmark v0.31.2):

```c
// Parsing
cmark_node *cmark_parse_document(const char *buffer, size_t len, int options);

// Rendering (all return caller-freed char*)
char *cmark_render_html(cmark_node *root, int options);
char *cmark_render_latex(cmark_node *root, int options, int width);
char *cmark_render_man(cmark_node *root, int options, int width);
char *cmark_render_commonmark(cmark_node *root, int options, int width);
char *cmark_render_xml(cmark_node *root, int options);

// Memory management
void cmark_node_free(cmark_node *node);
```

### CFFI Header Declarations (`cmark.cffi.h`)

```c
typedef struct cmark_node cmark_node;

cmark_node *cmark_parse_document(const char *buffer, size_t len, int options);
void cmark_node_free(cmark_node *node);

char *cmark_render_html(cmark_node *root, int options);
char *cmark_render_latex(cmark_node *root, int options, int width);
char *cmark_render_man(cmark_node *root, int options, int width);
char *cmark_render_commonmark(cmark_node *root, int options, int width);
char *cmark_render_xml(cmark_node *root, int options);

const char *cmark_version_string();

#define CMARK_OPT_DEFAULT ...
#define CMARK_OPT_SOURCEPOS ...
#define CMARK_OPT_HARDBREAKS ...
#define CMARK_OPT_UNSAFE ...
#define CMARK_OPT_NOBREAKS ...
#define CMARK_OPT_NORMALIZE ...
#define CMARK_OPT_VALIDATE_UTF8 ...
#define CMARK_OPT_SMART ...
```

## Python Wrapper Pattern

```python
# src/cmark_python/_cmark.py
from cmark_python._binding import ffi, lib


def _render(text: str, renderer, options: int = 0, width: int = 0) -> str:
    """Parse markdown and render with the given renderer function."""
    encoded = text.encode("utf-8")
    node = lib.cmark_parse_document(encoded, len(encoded), options)
    if node == ffi.NULL:
        raise MemoryError("Failed to parse document")
    try:
        if width is not None:
            result_ptr = renderer(node, options, width)
        else:
            result_ptr = renderer(node, options)
        if result_ptr == ffi.NULL:
            raise MemoryError("Failed to render document")
        result = ffi.string(result_ptr).decode("utf-8")
        lib.free(result_ptr)
        return result
    finally:
        lib.cmark_node_free(node)


def markdown_to_html(text: str, options: int = 0) -> str:
    encoded = text.encode("utf-8")
    node = lib.cmark_parse_document(encoded, len(encoded), options)
    if node == ffi.NULL:
        raise MemoryError("Failed to parse document")
    try:
        result_ptr = lib.cmark_render_html(node, options)
        result = ffi.string(result_ptr).decode("utf-8")
        lib.free(result_ptr)
        return result
    finally:
        lib.cmark_node_free(node)


def markdown_to_latex(text: str, options: int = 0, width: int = 0) -> str:
    return _render(text, lib.cmark_render_latex, options, width)


def markdown_to_man(text: str, options: int = 0, width: int = 0) -> str:
    return _render(text, lib.cmark_render_man, options, width)


def markdown_to_commonmark(text: str, options: int = 0, width: int = 0) -> str:
    return _render(text, lib.cmark_render_commonmark, options, width)


def markdown_to_xml(text: str, options: int = 0) -> str:
    encoded = text.encode("utf-8")
    node = lib.cmark_parse_document(encoded, len(encoded), options)
    if node == ffi.NULL:
        raise MemoryError("Failed to parse document")
    try:
        result_ptr = lib.cmark_render_xml(node, options)
        result = ffi.string(result_ptr).decode("utf-8")
        lib.free(result_ptr)
        return result
    finally:
        lib.cmark_node_free(node)
```

## Phase Plan

### Phase 1: MVP — All Renderers (Target: initial release)

1. Create repository with `pyproject.toml` (flit or setuptools + CFFI)
2. Vendor upstream `cmark` v0.31.2 C source into `third_party/cmark/`
3. Write CFFI build script that compiles the C library
4. Expose all 5 renderers with the simple `markdown_to_*` API
5. Options enum/IntFlag class
6. Tests covering all renderers against known inputs
7. CI with wheel building (see Wheel Building section below)
8. Publish to PyPI

### Phase 2: GFM Extensions

9. Switch vendored C source to `cmark-gfm` (GitHub's fork with extensions)
10. Expose extension registration API:
    - `table`
    - `strikethrough`
    - `autolink`
    - `tagfilter`
    - `tasklist`
11. Verify LaTeX output for GFM extensions (tables → `\begin{tabular}`, etc.)
12. Add `extensions` parameter to all `markdown_to_*` functions

### Phase 3: AST Access

13. Expose `cmark_parse_document` → opaque handle
14. AST iteration (`cmark_iter_*`)
15. AST manipulation (`cmark_node_*` accessors/mutators)
16. Separate `render_*` functions that take a pre-parsed AST
17. Enable parse-once, render-many workflows

## Wheel Building

### Strategy

Use [`cibuildwheel`](https://cibuildwheel.pypa.io/) to build pre-compiled wheels for all major platforms. Since cmark is pure C99 with zero external dependencies, cross-compilation is straightforward.

### Target Matrix

| OS | Architectures | Python Versions |
|----|---------------|-----------------|
| Linux (manylinux) | x86_64, aarch64 | 3.9, 3.10, 3.11, 3.12, 3.13 |
| macOS | x86_64, arm64 (universal2) | 3.9, 3.10, 3.11, 3.12, 3.13 |
| Windows | AMD64 | 3.9, 3.10, 3.11, 3.12, 3.13 |

### GitHub Actions Workflow

```yaml
# .github/workflows/wheels.yml
name: Build wheels

on:
  push:
    tags:
      - "v*"
  pull_request:
    branches: [main]

jobs:
  build_wheels:
    name: Build wheels on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install cibuildwheel
        run: pip install cibuildwheel==2.21.0

      - name: Build wheels
        run: python -m cibuildwheel --output-dir wheelhouse
        env:
          # Build for CPython only (no PyPy for now)
          CIBW_BUILD: "cp39-* cp310-* cp311-* cp312-* cp313-*"
          # Skip 32-bit builds and musllinux i686
          CIBW_SKIP: "*-win32 *-manylinux_i686 *-musllinux_i686"
          # Build universal2 wheels on macOS
          CIBW_ARCHS_MACOS: "x86_64 arm64"
          # Build x86_64 and aarch64 on Linux
          CIBW_ARCHS_LINUX: "x86_64 aarch64"
          # Test the built wheel
          CIBW_TEST_COMMAND: "pytest {project}/tests -x"
          CIBW_TEST_REQUIRES: "pytest"

      - uses: actions/upload-artifact@v4
        with:
          name: wheels-${{ matrix.os }}
          path: ./wheelhouse/*.whl

  build_sdist:
    name: Build source distribution
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Build sdist
        run: pip install build && python -m build --sdist

      - uses: actions/upload-artifact@v4
        with:
          name: sdist
          path: dist/*.tar.gz

  publish:
    name: Publish to PyPI
    needs: [build_wheels, build_sdist]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    permissions:
      id-token: write  # Trusted publishing
    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: wheels-*
          path: dist
          merge-multiple: true

      - uses: actions/download-artifact@v4
        with:
          name: sdist
          path: dist

      - uses: pypa/gh-action-pypi-publish@release/v1
```

### CFFI Build Script

```python
# src/cmark_python/_build_cmark.py
import os
from cffi import FFI

ffi = FFI()

# Read the CFFI declarations
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "cmark.cffi.h")) as f:
    ffi.cdef(f.read())

# Compile cmark C sources
cmark_dir = os.path.join(here, "..", "..", "third_party", "cmark", "src")
cmark_sources = [
    os.path.join(cmark_dir, f)
    for f in os.listdir(cmark_dir)
    if f.endswith(".c")
]

ffi.set_source(
    "cmark_python._binding",
    """
    #include "cmark.h"
    """,
    sources=cmark_sources,
    include_dirs=[cmark_dir],
    define_macros=[("CMARK_STATIC_DEFINE", None)],
)

if __name__ == "__main__":
    ffi.compile(verbose=True)
```

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68", "cffi>=1.15"]
build-backend = "setuptools.build_meta"

[project]
name = "cmark-python"
version = "0.1.0"
description = "Python bindings to cmark — CommonMark parsing and rendering (HTML, LaTeX, man, XML)"
readme = "README.md"
license = {text = "MIT AND BSD-2-Clause"}
requires-python = ">=3.9"
dependencies = ["cffi>=1.15"]
authors = [{name = "Rich Iannone"}]
classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: C",
    "Topic :: Text Processing :: Markup :: Markdown",
]

[project.urls]
Homepage = "https://github.com/posit-dev/cmark-python"
Issues = "https://github.com/posit-dev/cmark-python/issues"

[tool.setuptools]
packages = ["cmark_python"]
package-dir = {"" = "src"}

[tool.setuptools.package-data]
cmark_python = ["*.h"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| C library | Upstream `cmark` (not `cmark-gfm`) for Phase 1 | Cleaner, actively maintained by JMF, has all renderers |
| Binding | CFFI | Proven by `cmarkgfm`, good cross-platform support, ABI mode possible |
| Vendoring | Bundle C source | No system dependency required, same as R's approach |
| Python support | ≥3.9 | Match great-tables; cmark is C99, no Python-version constraints |
| Safety | Safe by default (`CMARK_OPT_UNSAFE` opt-in) | Match cmark's default; raw HTML stripped unless explicitly allowed |
| Package name | `cmark-python` | `commonmark` is taken (deprecated); clear what this wraps |

## Expected Properties

- **Zero Python dependencies** (only `cffi` at runtime)
- **Spec-compliant** (IS the reference implementation)
- **Security**: safe mode by default, fuzz-tested C code, no XSS vectors
- **Fast**: 10,000x faster than Markdown.pl
- **Portable**: C99, no external system deps, wheels for all platforms
- **Small**: cmark compiles to ~150KB shared library

## Test Strategy

Port test cases from:
1. R's `commonmark` package test suite
2. cmark's own `test/` directory (CommonMark spec tests)
3. Custom tests for Python-specific edge cases (Unicode, empty input, large docs)

```python
# Example tests
def test_latex_bold():
    assert markdown_to_latex("**bold**") == "\\textbf{bold}\n"

def test_latex_italic():
    assert markdown_to_latex("*italic*") == "\\emph{italic}\n"

def test_latex_heading():
    result = markdown_to_latex("# Title")
    assert "\\section{Title}" in result

def test_latex_link():
    result = markdown_to_latex("[text](http://example.com)")
    assert "\\href{http://example.com}{text}" in result

def test_latex_code():
    assert "\\texttt{code}" in markdown_to_latex("`code`")

def test_roundtrip_commonmark():
    md = "**bold** and *italic* and `code`"
    normalized = markdown_to_commonmark(md)
    # Re-parse normalized form — should produce same AST
    html1 = markdown_to_html(md)
    html2 = markdown_to_html(normalized)
    assert html1 == html2

def test_safe_mode_strips_raw_html():
    result = markdown_to_html("<script>alert('xss')</script>")
    assert "<script>" not in result

def test_unsafe_mode_allows_raw_html():
    from cmark_python import Options
    result = markdown_to_html("<div>hi</div>", options=Options.UNSAFE)
    assert "<div>hi</div>" in result
```

## References

- [cmark C library](https://github.com/commonmark/cmark) — upstream, BSD-2
- [cmark-gfm](https://github.com/github/cmark-gfm) — GitHub's fork with extensions
- [R commonmark package](https://github.com/r-lib/commonmark) — the model to follow
- [cmarkgfm (Python)](https://github.com/theacodes/cmarkgfm) — existing CFFI pattern to adapt
- [CommonMark spec](https://spec.commonmark.org/) — the specification
- [cibuildwheel docs](https://cibuildwheel.pypa.io/) — wheel building
