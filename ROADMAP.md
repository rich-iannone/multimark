# Roadmap

This document outlines longer-term ideas for multimark: features that would expand its
capabilities beyond the current render-to-string API.

---

## Planned — Near Term

Enhancements that build directly on existing infrastructure.

### Type Stubs / `py.typed` Marker

Add a `py.typed` marker and inline type annotations for better IDE support and static
analysis.

- PEP 561 compliant `py.typed` marker file in the package
- Full type annotations on all public functions and the `Options` enum
- Improved autocomplete, hover docs, and type checking in editors

---

## Planned — Medium Term

Features that expand the scope of what multimark can produce.

### Streaming / Incremental API

Expose the cmark parser object for large documents, allowing feed-based parsing without
buffering the entire input in memory.

- `Parser` class wrapping `cmark_parser_new` / `cmark_parser_feed` / `cmark_parser_finish`
- Extensions attachable at parser creation time
- Render from the finished AST node with any renderer
- Useful for processing very large Markdown files or streaming input

### AST Access

Let users walk the parsed tree from Python (not just render to a string).

- `parse()` function returning a `Node` wrapper around the cmark AST
- Tree traversal: `node.children`, `node.parent`, `node.next`, `node.prev`
- Node type introspection: `node.type`, `node.literal`, `node.url`, `node.title`
- Mutation support: insert, remove, and replace nodes before rendering
- Enables custom transformations, inspections, and selective rendering

---

## Feedback & Contributions

Have ideas for features not listed here? [Open an issue](https://github.com/rich-iannone/multimark/issues) with the `enhancement` label. Contributions to any planned item are welcome — check existing issues first to avoid duplication.

_This roadmap is a living document. It is updated as features ship and new priorities emerge._
