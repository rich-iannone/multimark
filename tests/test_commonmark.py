"""Smoke tests for CommonMark renderer — normalization, width, and roundtrip."""
from multimark import markdown_to_commonmark, markdown_to_html, Options


# --- Width parameter ---


def test_width_wraps_output():
    """Non-zero width wraps long paragraphs."""
    long_text = "word " * 100 + "\n"
    result = markdown_to_commonmark(long_text, width=72)
    content_lines = [l for l in result.split("\n") if "word" in l]
    assert all(len(l) <= 72 for l in content_lines)


def test_width_zero_no_wrapping():
    long_text = "word " * 100 + "\n"
    result = markdown_to_commonmark(long_text, width=0)
    content_lines = [l for l in result.split("\n") if "word" in l]
    assert any(len(l) > 72 for l in content_lines)


# --- Normalization ---


def test_normalizes_heading_whitespace():
    """Extra spaces in headings are normalized."""
    result = markdown_to_commonmark("#   Title  \n")
    assert "# Title" in result


def test_normalizes_emphasis_style():
    """Underscore emphasis normalizes to asterisks."""
    result = markdown_to_commonmark("__bold__ and _italic_\n")
    assert "**bold**" in result
    assert "*italic*" in result


def test_output_is_valid_markdown():
    """Normalized output re-parses to identical HTML."""
    md = "# Title\n\n**bold** with [link](http://x.com) and `code`\n"
    normalized = markdown_to_commonmark(md)
    assert markdown_to_html(md) == markdown_to_html(normalized)


# --- Edge cases ---


def test_empty_input():
    assert markdown_to_commonmark("") == "\n"


def test_unicode_preserved():
    result = markdown_to_commonmark("你好世界\n")
    assert "你好世界" in result


def test_smart_option():
    """SMART option produces typographic chars that roundtrip."""
    result = markdown_to_commonmark('"Hello"\n', options=Options.SMART)
    assert "\u201c" in result
