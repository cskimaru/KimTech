"""A tiny, safe text format for guide articles.

Everything is HTML-escaped first, so nothing typed in the admin can inject markup or
scripts (the site's strict CSP would block inline scripts anyway). Then a few simple
patterns are turned into HTML:

    ## Heading            -> <h2>
    ### Smaller heading   -> <h3>
    - item                -> bullet list (every line of the block starts with "- ")
    **bold**              -> <strong>
    [text](url)           -> link. url must start with "/" or "https://".
                             Links to /go/... get rel="sponsored nofollow".
                             Other https:// links open in a new tab.
    anything else         -> paragraph (blank line between paragraphs)
"""

import re

from django.utils.html import escape
from django.utils.safestring import mark_safe

_LINK = re.compile(r"\[([^\]\n]+)\]\((/[^\s)]*|https://[^\s)]+)\)")
_BOLD = re.compile(r"\*\*([^*\n]+)\*\*")


def _link(match):
    text, url = match.group(1), match.group(2)
    if url.startswith("/go/"):
        return f'<a href="{url}" rel="sponsored nofollow noopener" target="_blank">{text}</a>'
    if url.startswith("https://"):
        return f'<a href="{url}" rel="noopener" target="_blank">{text}</a>'
    return f'<a href="{url}">{text}</a>'


def _inline(text):
    text = _LINK.sub(_link, text)
    return _BOLD.sub(r"<strong>\1</strong>", text)


def render_article(source):
    html = []
    for block in re.split(r"\n\s*\n", escape(source or "").replace("\r\n", "\n").strip()):
        lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
        if not lines:
            continue
        if len(lines) == 1 and lines[0].startswith("### "):
            html.append(f"<h3>{_inline(lines[0][4:])}</h3>")
        elif len(lines) == 1 and lines[0].startswith("## "):
            html.append(f"<h2>{_inline(lines[0][3:])}</h2>")
        elif all(line.startswith("- ") for line in lines):
            items = "".join(f"<li>{_inline(line[2:])}</li>" for line in lines)
            html.append(f"<ul>{items}</ul>")
        else:
            html.append(f"<p>{_inline(' '.join(lines))}</p>")
    # Safe: the source was HTML-escaped above; only fixed tags and checked URLs are added.
    return mark_safe("\n".join(html))  # nosec B308 B703


def has_affiliate_links(source):
    return "](/go/" in (source or "")
