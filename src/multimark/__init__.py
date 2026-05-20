"""multimark — Python bindings to the cmark-gfm CommonMark/GFM C library.

Provides parsing and rendering of CommonMark and GitHub Flavored Markdown
to HTML, LaTeX, groff man, XML, and normalized CommonMark.
"""
from enum import IntFlag
from importlib.metadata import PackageNotFoundError, version as _get_version

try:
    __version__ = _get_version("multimark")
except PackageNotFoundError:
    __version__ = "0.0.0"

from multimark._cmark import (
    markdown_to_html,
    markdown_to_latex,
    markdown_to_man,
    markdown_to_commonmark,
    markdown_to_xml,
    cmark_version,
    VALID_EXTENSIONS,
)
from multimark._binding import lib


class Options(IntFlag):
    """CommonMark/GFM parsing/rendering options."""

    DEFAULT = lib.CMARK_OPT_DEFAULT
    SOURCEPOS = lib.CMARK_OPT_SOURCEPOS
    HARDBREAKS = lib.CMARK_OPT_HARDBREAKS
    SAFE = lib.CMARK_OPT_SAFE
    UNSAFE = lib.CMARK_OPT_UNSAFE
    NOBREAKS = lib.CMARK_OPT_NOBREAKS
    NORMALIZE = lib.CMARK_OPT_NORMALIZE
    VALIDATE_UTF8 = lib.CMARK_OPT_VALIDATE_UTF8
    SMART = lib.CMARK_OPT_SMART
    # GFM-specific options
    GITHUB_PRE_LANG = lib.CMARK_OPT_GITHUB_PRE_LANG
    LIBERAL_HTML_TAG = lib.CMARK_OPT_LIBERAL_HTML_TAG
    FOOTNOTES = lib.CMARK_OPT_FOOTNOTES
    STRIKETHROUGH_DOUBLE_TILDE = lib.CMARK_OPT_STRIKETHROUGH_DOUBLE_TILDE
    TABLE_PREFER_STYLE_ATTRIBUTES = lib.CMARK_OPT_TABLE_PREFER_STYLE_ATTRIBUTES
    FULL_INFO_STRING = lib.CMARK_OPT_FULL_INFO_STRING


__all__ = [
    "markdown_to_html",
    "markdown_to_latex",
    "markdown_to_man",
    "markdown_to_commonmark",
    "markdown_to_xml",
    "cmark_version",
    "Options",
    "VALID_EXTENSIONS",
    "__version__",
]
