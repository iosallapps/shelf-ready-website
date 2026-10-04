"""Build the shared parts of every page, and the legal pages from the app's own legal texts.

    python3 _tools/build_pages.py

- index.html and support.html are edited by hand. Their head, header and footer sit between
  <!-- build:NAME --> ... <!-- /build:NAME --> markers and are rewritten from partials.py.
- privacy.html and terms.html are generated in full from the documents bundled in the app,
  ~/Developer/ShelfReady/StudioApp/Legal/*.md, so the site and the app cannot disagree.
  Rerun this script whenever those files change.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import partials  # noqa: E402

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGAL_DIR = os.path.expanduser("~/Developer/ShelfReady/StudioApp/Legal")

HAND_PAGES = {
    "index.html": (
        "ShelfReady: Product Photos and Background Remover",
        "Take a photo of what you sell. ShelfReady removes the background on your iPhone and sets "
        "the item on a clean studio backdrop with a soft shadow, sized for your listing.",
        "",
    ),
    "support.html": (
        "Support and FAQ | ShelfReady",
        "Help with ShelfReady: removing backgrounds, fixing a cutout, free saves, restoring "
        "purchases, managing your subscription, deleting photos and privacy choices.",
        "support.html",
    ),
}

LEGAL_PAGES = {
    "privacy.html": ("privacy-policy.md", "Privacy Policy | ShelfReady",
                     "How ShelfReady handles your data. Your photos are edited on your device and never uploaded."),
    "terms.html": ("terms-of-use.md", "Terms of Use | ShelfReady",
                   "The terms for using ShelfReady, including free saves, subscriptions and the lifetime purchase."),
}

FORBIDDEN = ["\u2014", "\u2013"]  # no em or en dashes anywhere


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)


def markdown_to_html(source):
    """The small Markdown subset the legal files use: #, ##, paragraphs, - lists, bold, links."""
    lines = source.splitlines()
    title = lines[0].lstrip("# ").strip()
    blocks, paragraph, items = [], [], []

    def flush():
        if paragraph:
            blocks.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()
        if items:
            blocks.append("<ul>\n" + "\n".join(f"<li>{inline(i)}</li>" for i in items) + "\n</ul>")
            items.clear()

    for raw in lines[1:]:
        line = raw.strip()
        if not line:
            flush()
        elif line.startswith("## "):
            flush()
            blocks.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            if paragraph:
                flush()
            items.append(line[2:])
        elif items and raw.startswith("  "):
            items[-1] += " " + line
        else:
            paragraph.append(line)
    flush()
    return title, blocks


def legal_page(md_name, page_title, description, path):
    with open(os.path.join(LEGAL_DIR, md_name), encoding="utf-8") as f:
        title, blocks = markdown_to_html(f.read())
    # The first two paragraphs are the byline and the date: they become the page header.
    byline = re.sub(r"<.*?>", "", blocks.pop(0))
    updated = re.sub(r"<.*?>", "", blocks.pop(0))
    body = "\n                ".join(blocks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    {partials.head(page_title, description, path)}
</head>
<body>
    <a class="skip-link" href="#main">Skip to content</a>
    {partials.HEADER}

    <main id="main" class="doc">
        <div class="container">
            <header class="doc-head">
                <h1>{html.escape(title)}</h1>
                <p class="doc-meta">{html.escape(byline)}</p>
                <p class="doc-meta">{html.escape(updated)}</p>
            </header>
            <div class="doc-body">
                {body}
            </div>
        </div>
    </main>

    {partials.FOOTER}
</body>
</html>
"""


def replace_region(page, name, content):
    pattern = re.compile(rf"(<!-- build:{name} -->)(.*?)(\s*<!-- /build:{name} -->)", re.S)
    if not pattern.search(page):
        raise SystemExit(f"missing build:{name} marker")
    return pattern.sub(lambda m: m.group(1) + "\n    " + content + m.group(3), page)


def main():
    for name, (title, description, path) in HAND_PAGES.items():
        file = os.path.join(SITE_DIR, name)
        with open(file, encoding="utf-8") as f:
            page = f.read()
        page = replace_region(page, "head", partials.head(title, description, path))
        page = replace_region(page, "header", partials.HEADER)
        page = replace_region(page, "footer", partials.FOOTER)
        with open(file, "w", encoding="utf-8") as f:
            f.write(page)
        print("updated", name)

    for name, (md_name, title, description) in LEGAL_PAGES.items():
        with open(os.path.join(SITE_DIR, name), "w", encoding="utf-8") as f:
            f.write(legal_page(md_name, title, description, name))
        print("generated", name)

    problems = 0
    for name in list(HAND_PAGES) + list(LEGAL_PAGES):
        with open(os.path.join(SITE_DIR, name), encoding="utf-8") as f:
            text = f.read()
        for bad in FORBIDDEN:
            if bad in text:
                print(f"FORBIDDEN {bad!r} in {name}")
                problems += 1
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
