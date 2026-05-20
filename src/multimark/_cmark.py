"""Low-level CFFI wrapper around the cmark-gfm C library."""
from __future__ import annotations

from typing import Sequence

from multimark._binding import ffi, lib

# Register all built-in GFM extensions once at import time.
lib.cmark_gfm_core_extensions_ensure_registered()

# Valid extension names recognized by cmark-gfm.
VALID_EXTENSIONS = frozenset(
    ["table", "strikethrough", "autolink", "tagfilter", "tasklist"]
)


def _build_options(
    options: int,
    hardbreaks: bool,
    smart: bool,
    normalize: bool,
    sourcepos: bool,
    unsafe: bool,
    footnotes: bool,
) -> int:
    """Combine named boolean flags with a raw options bitmask."""
    if hardbreaks:
        options |= lib.CMARK_OPT_HARDBREAKS
    if smart:
        options |= lib.CMARK_OPT_SMART
    if normalize:
        options |= lib.CMARK_OPT_NORMALIZE
    if sourcepos:
        options |= lib.CMARK_OPT_SOURCEPOS
    if unsafe:
        options |= lib.CMARK_OPT_UNSAFE
    if footnotes:
        options |= lib.CMARK_OPT_FOOTNOTES
    return options


def _parse_with_extensions(
    encoded: bytes, opts: int, extensions: Sequence[str]
):
    """Parse markdown using the streaming parser with extensions attached.

    Returns (node, parser) — caller must free both.
    """
    parser = lib.cmark_parser_new(opts)
    if parser == ffi.NULL:
        raise MemoryError("Failed to create parser")

    for ext_name in extensions:
        ext = lib.cmark_find_syntax_extension(ext_name.encode("utf-8"))
        if ext == ffi.NULL:
            lib.cmark_parser_free(parser)
            raise ValueError(f"Unknown extension: {ext_name!r}")
        lib.cmark_parser_attach_syntax_extension(parser, ext)

    lib.cmark_parser_feed(parser, encoded, len(encoded))
    node = lib.cmark_parser_finish(parser)
    if node == ffi.NULL:
        lib.cmark_parser_free(parser)
        raise MemoryError("Failed to parse document")
    return node, parser


def markdown_to_html(
    text: str,
    *,
    hardbreaks: bool = False,
    smart: bool = False,
    normalize: bool = False,
    sourcepos: bool = False,
    unsafe: bool = False,
    footnotes: bool = False,
    extensions: Sequence[str] = (),
    options: int = 0,
) -> str:
    """Parse CommonMark/GFM and render as HTML.

    Parameters
    ----------
    text
        Markdown text to render.
    hardbreaks
        Treat newlines as hard line breaks.
    smart
        Use smart punctuation (curly quotes, em/en dashes, ellipses).
    normalize
        Consolidate adjacent text nodes.
    sourcepos
        Include source position attributes in output.
    unsafe
        Allow raw HTML to pass through (default strips it).
    footnotes
        Parse footnotes.
    extensions
        GFM extensions to enable: "table", "strikethrough", "autolink",
        "tagfilter", "tasklist".
    options
        Raw cmark options bitmask (combined with named flags via OR).
    """
    opts = _build_options(options, hardbreaks, smart, normalize, sourcepos, unsafe, footnotes)
    encoded = text.encode("utf-8")

    if extensions:
        node, parser = _parse_with_extensions(encoded, opts, extensions)
        ext_list = lib.cmark_parser_get_syntax_extensions(parser)
        try:
            result_ptr = lib.cmark_render_html(node, opts, ext_list)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)
            lib.cmark_parser_free(parser)
    else:
        node = lib.cmark_parse_document(encoded, len(encoded), opts)
        if node == ffi.NULL:
            raise MemoryError("Failed to parse document")
        try:
            result_ptr = lib.cmark_render_html(node, opts, ffi.NULL)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)


def markdown_to_xml(
    text: str,
    *,
    hardbreaks: bool = False,
    smart: bool = False,
    normalize: bool = False,
    sourcepos: bool = False,
    unsafe: bool = False,
    footnotes: bool = False,
    extensions: Sequence[str] = (),
    options: int = 0,
) -> str:
    """Parse CommonMark/GFM and render as XML.

    Parameters
    ----------
    text
        Markdown text to render.
    hardbreaks
        Treat newlines as hard line breaks.
    smart
        Use smart punctuation (curly quotes, em/en dashes, ellipses).
    normalize
        Consolidate adjacent text nodes.
    sourcepos
        Include source position attributes in output.
    unsafe
        Allow raw HTML to pass through.
    footnotes
        Parse footnotes.
    extensions
        GFM extensions to enable.
    options
        Raw cmark options bitmask (combined with named flags via OR).
    """
    opts = _build_options(options, hardbreaks, smart, normalize, sourcepos, unsafe, footnotes)
    encoded = text.encode("utf-8")

    if extensions:
        node, parser = _parse_with_extensions(encoded, opts, extensions)
        try:
            result_ptr = lib.cmark_render_xml(node, opts)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)
            lib.cmark_parser_free(parser)
    else:
        node = lib.cmark_parse_document(encoded, len(encoded), opts)
        if node == ffi.NULL:
            raise MemoryError("Failed to parse document")
        try:
            result_ptr = lib.cmark_render_xml(node, opts)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)


def markdown_to_latex(
    text: str,
    *,
    hardbreaks: bool = False,
    smart: bool = False,
    normalize: bool = False,
    unsafe: bool = False,
    footnotes: bool = False,
    extensions: Sequence[str] = (),
    width: int = 0,
    options: int = 0,
) -> str:
    """Parse CommonMark/GFM and render as LaTeX.

    Parameters
    ----------
    text
        Markdown text to render.
    hardbreaks
        Treat newlines as hard line breaks.
    smart
        Use smart punctuation (curly quotes, em/en dashes, ellipses).
    normalize
        Consolidate adjacent text nodes.
    unsafe
        Allow raw HTML to pass through.
    footnotes
        Parse footnotes.
    extensions
        GFM extensions to enable.
    width
        Wrap width (0 = no wrapping).
    options
        Raw cmark options bitmask (combined with named flags via OR).
    """
    opts = _build_options(options, hardbreaks, smart, normalize, False, unsafe, footnotes)
    encoded = text.encode("utf-8")

    if extensions:
        node, parser = _parse_with_extensions(encoded, opts, extensions)
        try:
            result_ptr = lib.cmark_render_latex(node, opts, width)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)
            lib.cmark_parser_free(parser)
    else:
        node = lib.cmark_parse_document(encoded, len(encoded), opts)
        if node == ffi.NULL:
            raise MemoryError("Failed to parse document")
        try:
            result_ptr = lib.cmark_render_latex(node, opts, width)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)


def markdown_to_man(
    text: str,
    *,
    hardbreaks: bool = False,
    smart: bool = False,
    normalize: bool = False,
    unsafe: bool = False,
    footnotes: bool = False,
    extensions: Sequence[str] = (),
    width: int = 0,
    options: int = 0,
) -> str:
    """Parse CommonMark/GFM and render as groff man page.

    Parameters
    ----------
    text
        Markdown text to render.
    hardbreaks
        Treat newlines as hard line breaks.
    smart
        Use smart punctuation (curly quotes, em/en dashes, ellipses).
    normalize
        Consolidate adjacent text nodes.
    unsafe
        Allow raw HTML to pass through.
    footnotes
        Parse footnotes.
    extensions
        GFM extensions to enable.
    width
        Wrap width (0 = no wrapping).
    options
        Raw cmark options bitmask (combined with named flags via OR).
    """
    opts = _build_options(options, hardbreaks, smart, normalize, False, unsafe, footnotes)
    encoded = text.encode("utf-8")

    if extensions:
        node, parser = _parse_with_extensions(encoded, opts, extensions)
        try:
            result_ptr = lib.cmark_render_man(node, opts, width)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)
            lib.cmark_parser_free(parser)
    else:
        node = lib.cmark_parse_document(encoded, len(encoded), opts)
        if node == ffi.NULL:
            raise MemoryError("Failed to parse document")
        try:
            result_ptr = lib.cmark_render_man(node, opts, width)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)


def markdown_to_commonmark(
    text: str,
    *,
    hardbreaks: bool = False,
    smart: bool = False,
    normalize: bool = False,
    unsafe: bool = False,
    footnotes: bool = False,
    extensions: Sequence[str] = (),
    width: int = 0,
    options: int = 0,
) -> str:
    """Parse CommonMark/GFM and render back as normalized CommonMark.

    Parameters
    ----------
    text
        Markdown text to render.
    hardbreaks
        Treat newlines as hard line breaks.
    smart
        Use smart punctuation (curly quotes, em/en dashes, ellipses).
    normalize
        Consolidate adjacent text nodes.
    unsafe
        Allow raw HTML to pass through.
    footnotes
        Parse footnotes.
    extensions
        GFM extensions to enable.
    width
        Wrap width (0 = no wrapping).
    options
        Raw cmark options bitmask (combined with named flags via OR).
    """
    opts = _build_options(options, hardbreaks, smart, normalize, False, unsafe, footnotes)
    encoded = text.encode("utf-8")

    if extensions:
        node, parser = _parse_with_extensions(encoded, opts, extensions)
        try:
            result_ptr = lib.cmark_render_commonmark(node, opts, width)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)
            lib.cmark_parser_free(parser)
    else:
        node = lib.cmark_parse_document(encoded, len(encoded), opts)
        if node == ffi.NULL:
            raise MemoryError("Failed to parse document")
        try:
            result_ptr = lib.cmark_render_commonmark(node, opts, width)
            if result_ptr == ffi.NULL:
                raise MemoryError("Failed to render document")
            result = ffi.string(result_ptr).decode("utf-8", errors="replace")
            lib.free(result_ptr)
            return result
        finally:
            lib.cmark_node_free(node)


def cmark_version() -> str:
    """Return the cmark library version string."""
    return ffi.string(lib.cmark_version_string()).decode("utf-8")
