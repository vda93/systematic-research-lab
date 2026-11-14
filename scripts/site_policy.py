"""Publication boundary for the small, buildless research website."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import re


PAGES = {f'docs/{slug}.html' for slug in ('index', 'orb', 'ebp', 'orbindex', 'macroimpulse')}
CSS = 'docs/site.css'
MARKER = 'docs/.nojekyll'
REPOSITORY = 'https://github.com/vda93/systematic-research-lab'
SOURCE_PREFIX = REPOSITORY + '/blob/main/'

# These exact original public SVGs were approved for inclusion in the website.
# A directly navigable SVG is a document. Its path alone cannot authorize it.
PLOT_HASHES = {
    'docs/plots/orb-summary.svg': '839c20e775fdeafe20e7ff2d6276e512dd3fdb8ef9eedfdccd291ca32ce30a88',
    'docs/plots/orb-gold-economics.svg': '4415d05be3e792cdb5338cde11fe7ba31ca4b1b54a8c141b0fd08027c204528e',
    'docs/plots/ebp-order-policy.svg': '58dc8dbc6a83e38f92c0d5c25c65626a5be28d3ea79af95855381f84ee298a9e',
    'docs/plots/ebp-native-timeframe.svg': 'a034c25a6ebd1bff0bf799825e5f4483dedcb652ad761e8e0c53be04d1a6ed22',
    'docs/plots/orbindex-economics.svg': '921b95a94462d3220fc019a8ea5abec557b506d1848bd62d8d688b4d41953344',
    'docs/plots/macro-mechanics.svg': '9e795b4b4b6898248cb0af9d56a704de5d6ddabef0ec7cfe585f37ffec560d3b',
    'docs/plots/macro-baseline.svg': '9254bbb53deab6f418f8095915e7de01fbd2e58337b879f5882b0739b1448317',
}
# Review the complete local CSS before authorizing its bytes. This also covers
# resource-bearing CSS syntax without maintaining a partial CSS parser.
CSS_SHA256 = '649b29995ae3c9d830b380185d29b5554074fc75e64a16149048aefacbe85faf'

TAGS = set('html head body title meta link header div span nav main section article h1 h2 h3 '
           'p strong em code aside figure img figcaption footer ul li a'.split())
VOID = {'meta', 'link', 'img'}
COMMON_ATTRS = {'class', 'id', 'aria-label', 'aria-labelledby', 'aria-hidden', 'aria-current', 'tabindex'}
ATTRS = {
    'html': {'lang'}, 'meta': {'charset', 'name', 'content'}, 'link': {'rel', 'href'},
    'a': {'href'}, 'img': {'src', 'alt', 'loading', 'width', 'height'},
}
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]*')
SOURCE_PATH = re.compile(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*(?:/[A-Za-z0-9_-][A-Za-z0-9_.-]*)*')
START_TAG = re.compile(r"""<[A-Za-z][A-Za-z0-9]*(?:\s+[A-Za-z][A-Za-z0-9-]*\s*=\s*(?:"[^"<>]*"|'[^'<>]*'))*\s*/?>""")


class SitePage(HTMLParser):
    """Accept only the passive markup emitted by the static renderer."""

    def __init__(self, name: str, text: str):
        super().__init__(convert_charrefs=False)
        self.name = name
        self.ids: set[str] = set()
        self.references: list[tuple[str, str]] = []
        self.errors: list[str] = []
        self._stack: list[str] = []
        self._count: Counter[str] = Counter()
        try:
            self.feed(text)
            self.close()
        except (ValueError, AssertionError):
            self.errors.append('malformed markup')
        if self._stack or self._count['h1'] != 1 or self._count['main'] != 1:
            self.errors.append('invalid document structure or landmarks')
        if any(dest == name and fragment and fragment not in self.ids for dest, fragment in self.references):
            self.errors.append('missing in-page target')

    def handle_decl(self, decl):
        if decl.lower() != 'doctype html':
            self.errors.append('unapproved declaration')

    def unknown_decl(self, data):
        self.errors.append('unapproved declaration')

    def handle_comment(self, data):
        self.errors.append('unexpected markup comment')

    def handle_pi(self, data):
        self.errors.append('unapproved processing instruction')

    def handle_data(self, data):
        if '<' in data:
            self.errors.append('unexpected markup in text')

    def handle_starttag(self, tag, attrs):
        if tag not in TAGS or not START_TAG.fullmatch(self.get_starttag_text()):
            self.errors.append('unapproved tag or attribute syntax')
            return
        attributes = dict(attrs)
        if len(attributes) != len(attrs) or attributes.keys() - (COMMON_ATTRS | ATTRS.get(tag, set())):
            self.errors.append('unapproved or repeated attribute')
        self._count[tag] += 1
        if tag not in VOID:
            self._stack.append(tag)
        if 'id' in attributes:
            identifier = attributes['id']
            if not ID.fullmatch(identifier) or identifier in self.ids:
                self.errors.append('invalid or duplicate ID')
            self.ids.add(identifier)
        if tag == 'meta':
            if not (attributes == {'charset': 'utf-8'} or (
                    attributes.keys() == {'name', 'content'} and
                    attributes['name'] in {'viewport', 'color-scheme', 'description'})):
                self.errors.append('unapproved metadata')
        elif tag == 'link':
            if attributes != {'rel': 'stylesheet', 'href': 'site.css'}:
                self.errors.append('unapproved stylesheet')
            self.references.append((CSS, ''))
        elif tag == 'img':
            path = 'docs/' + attributes.get('src', '')
            if path not in PLOT_HASHES or not attributes.get('alt', '').strip():
                self.errors.append('image requires an approved local figure and description')
            self.references.append((path, ''))
        elif tag == 'a':
            self._link(attributes.get('href', ''))

    def handle_startendtag(self, tag, attrs):
        if tag not in VOID:
            self.errors.append('unexpected self-closing tag')
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if not self._stack or self._stack.pop() != tag:
            self.errors.append('unbalanced tags')

    def _link(self, target: str):
        if target == REPOSITORY:
            return
        base, separator, fragment = target.partition('#')
        if separator and not ID.fullmatch(fragment):
            self.errors.append('invalid fragment')
            return
        if base.startswith(SOURCE_PREFIX):
            dest = base[len(SOURCE_PREFIX):]
            if not SOURCE_PATH.fullmatch(dest) or (fragment and not dest.endswith('.md')):
                self.errors.append('unapproved repository source')
                return
        elif target.startswith('#'):
            dest = self.name
        else:
            dest = 'docs/' + base
            if dest not in PAGES and not (dest in PLOT_HASHES and not fragment):
                self.errors.append('unapproved navigation target')
                return
        self.references.append((dest, fragment))
