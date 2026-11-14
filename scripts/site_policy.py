"""Publication boundary for the small, buildless research website."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import re


PAGES = {f'docs/{slug}.html' for slug in ('index', 'orbindex', 'macroimpulse')}
CSS = 'docs/site.css'
MARKER = 'docs/.nojekyll'
REPOSITORY = 'https://github.com/vda93/systematic-research-lab'
SOURCE_PREFIX = REPOSITORY + '/blob/main/'

# These exact original public SVGs were approved for inclusion in the website.
# A directly navigable SVG is a document. Its path alone cannot authorize it.
PLOT_HASHES = {
    'docs/plots/orbindex-curves.svg': 'ba936bf42ac818587c19e386a1839b2d1633224b663fd854792be2861b5ccd75',
    'docs/plots/orbindex-economics.svg': '921b95a94462d3220fc019a8ea5abec557b506d1848bd62d8d688b4d41953344',
    'docs/plots/orbindex-forensics.svg': 'b5daa419c717d20a5795cbd72d26c61f9fd40e2a597e8dd5b9ecee6ba2c7aa1e',
    'docs/plots/orbindex-jp-uk-heatmaps.svg': 'c22892702b39107418dca4dc616984b0934d2028fdff17f552fd2c6208762ed7',
    'docs/plots/orbindex-portfolios.svg': '1269c88dbcc4d615d50689fd214006c29cdc5193bc0963876981c212e2717fd9',
    'docs/plots/orbindex-search.svg': '0c8df6ca3c5a9b778f35b496dcf10cb4805e2c884f43b3ed41f30f28ef9c0c43',
    'docs/plots/macro-mechanics.svg': '9e795b4b4b6898248cb0af9d56a704de5d6ddabef0ec7cfe585f37ffec560d3b',
    'docs/plots/macro-baseline.svg': '9254bbb53deab6f418f8095915e7de01fbd2e58337b879f5882b0739b1448317',
    'docs/plots/macro-spread-filter.svg': '43b647aca195d82bfa4a1431165324cd8452136e8fd76d42ff2728a517186c0d',
    'docs/plots/macro-sequential.svg': 'ea51c8e4c4df58421a59c28b4eed1e5de23066b9c8fdeed74b68d7345a2f31bc',
}
# Review the complete local CSS before authorizing its bytes. This also covers
# resource-bearing CSS syntax without maintaining a partial CSS parser.
CSS_SHA256 = 'e1201d1d36947ad02503bf79d73ba141669190ebe5012842cd6c7c061f9467dd'

TAGS = set('html head body title meta link header div span nav main section article h1 h2 h3 '
           'p strong em code aside figure img figcaption footer ul li a table thead tbody tr th td'.split())
VOID = {'meta', 'link', 'img'}
COMMON_ATTRS = {'class', 'id', 'aria-label', 'aria-labelledby', 'aria-hidden', 'aria-current', 'tabindex'}
ATTRS = {
    'th': {'scope'}, 'html': {'lang'}, 'meta': {'charset', 'name', 'content'}, 'link': {'rel', 'href'},
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
        if tag == 'th' and attributes.get('scope', 'col') != 'col':
            self.errors.append('unapproved table heading scope')
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
