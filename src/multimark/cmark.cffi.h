/* Core types */
typedef struct cmark_node cmark_node;
typedef struct cmark_parser cmark_parser;
typedef struct cmark_syntax_extension cmark_syntax_extension;
typedef struct _cmark_llist {
    struct _cmark_llist *next;
    void *data;
} cmark_llist;

/* Parser API (streaming with extension support) */
cmark_parser *cmark_parser_new(int options);
void cmark_parser_free(cmark_parser *parser);
void cmark_parser_feed(cmark_parser *parser, const char *buffer, size_t len);
cmark_node *cmark_parser_finish(cmark_parser *parser);
int cmark_parser_attach_syntax_extension(cmark_parser *parser, cmark_syntax_extension *extension);
cmark_llist *cmark_parser_get_syntax_extensions(cmark_parser *parser);

/* Simple parsing (no extensions) */
cmark_node *cmark_parse_document(const char *buffer, size_t len, int options);
void cmark_node_free(cmark_node *node);

/* Extension registration */
void cmark_gfm_core_extensions_ensure_registered(void);
cmark_syntax_extension *cmark_find_syntax_extension(const char *name);

/* Rendering */
char *cmark_render_html(cmark_node *root, int options, cmark_llist *extensions);
char *cmark_render_latex(cmark_node *root, int options, int width);
char *cmark_render_man(cmark_node *root, int options, int width);
char *cmark_render_commonmark(cmark_node *root, int options, int width);
char *cmark_render_xml(cmark_node *root, int options);

const char *cmark_version_string(void);

void free(void *ptr);

/* Core options */
#define CMARK_OPT_DEFAULT ...
#define CMARK_OPT_SOURCEPOS ...
#define CMARK_OPT_HARDBREAKS ...
#define CMARK_OPT_SAFE ...
#define CMARK_OPT_UNSAFE ...
#define CMARK_OPT_NOBREAKS ...
#define CMARK_OPT_NORMALIZE ...
#define CMARK_OPT_VALIDATE_UTF8 ...
#define CMARK_OPT_SMART ...

/* GFM-specific options */
#define CMARK_OPT_GITHUB_PRE_LANG ...
#define CMARK_OPT_LIBERAL_HTML_TAG ...
#define CMARK_OPT_FOOTNOTES ...
#define CMARK_OPT_STRIKETHROUGH_DOUBLE_TILDE ...
#define CMARK_OPT_TABLE_PREFER_STYLE_ATTRIBUTES ...
#define CMARK_OPT_FULL_INFO_STRING ...
