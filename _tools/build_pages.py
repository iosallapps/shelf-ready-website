"""Build the shared parts of every page, and the legal pages from the app's own legal texts.

    python3 _tools/build_pages.py

- index.html and support.html are edited by hand. Their head, header and footer sit between
  <!-- build:NAME --> ... <!-- /build:NAME --> markers and are rewritten from partials.py.
- privacy.html, terms.html and ro/privacy.html, ro/terms.html wrap the legal fragments in
  _tools/legal/, produced by ~/Developer/visto-apps/tools/legal/adapters/fragments.py from
  apps/shelfready.json (facts read in the app's code). Copy the four fragments here after a
  facts change, then rerun this script.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import partials  # noqa: E402
import jsonld  # noqa: E402

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGAL_DIR = os.path.join(SITE_DIR, "_tools", "legal")

HAND_PAGES = {
    "index.html": (
        "ShelfReady: Product Photos and Background Remover",
        "Take a photo of what you sell. ShelfReady removes the background and sets it on a clean studio backdrop with a soft shadow. On iPhone, nothing uploaded. Free.",
        "",
    ),
    "support.html": (
        "Support | ShelfReady Product Photos",
        "Help with ShelfReady: removing backgrounds, fixing a cutout, free saves, restoring purchases, managing a subscription, deleting photos and privacy choices.",
        "support.html",
    ),
    "404.html": (
        "Page not found | ShelfReady",
        "This page is not on shelfreadyapp.com. Go back to ShelfReady, the product photo app that removes the background on your iPhone.",
        "404.html",
    ),
}

LEGAL_PAGES = {
    "privacy.html": ("privacy", "en", "Privacy Policy | ShelfReady",
                     "How ShelfReady handles your data. Your product photos are edited on your device and never uploaded. What the ads, analytics and purchases services receive."),
    "terms.html": ("terms", "en", "Terms of Use | ShelfReady",
                   "The terms for using ShelfReady, the product photo app: free saves, subscriptions, the lifetime purchase, ads and your responsibility for the photos you publish."),
    "ro/privacy.html": ("privacy", "ro", "Politica de confidențialitate | ShelfReady",
                        "Cum tratează ShelfReady datele tale. Pozele de produs rămân pe dispozitiv și nu sunt încărcate. Ce primesc serviciile de reclame, statistici și achiziții."),
    "ro/terms.html": ("terms", "ro", "Termeni de utilizare | ShelfReady",
                      "Termenii de utilizare ShelfReady, aplicația pentru poze de produs: salvări gratuite, abonamente, achiziția pe viață, reclame și pozele publicate."),
}

OTHER_LANG = {
    ("privacy", "en"): ("ro/privacy.html", "Română", "ro"),
    ("terms", "en"): ("ro/terms.html", "Română", "ro"),
    ("privacy", "ro"): ("../privacy.html", "English", "en"),
    ("terms", "ro"): ("../terms.html", "English", "en"),
}

FORBIDDEN = ["\u2014", "\u2013"]  # no em or en dashes anywhere


def legal_page(kind, lang, page_title, description, path):
    with open(os.path.join(LEGAL_DIR, f"{kind}.{lang}.html"), encoding="utf-8") as f:
        body = f.read()
    prefix = "../" if path.startswith("ro/") else ""
    other_href, other_label, other_lang = OTHER_LANG[(kind, lang)]
    en_path, ro_path = (f"{kind}.html", f"ro/{kind}.html")
    alternates = [("en", en_path), ("ro", ro_path), ("x-default", en_path)]
    head = partials.head(page_title, description, path, locale="ro_RO" if lang == "ro" else "en_US", alternates=alternates)
    if prefix:
        head = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)', r'\1="' + prefix, head)
    header = partials.header()
    footer = partials.FOOTER
    if prefix:
        header = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)(\./)?', r'\1="' + prefix, header)
        footer = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)(\./)?', r'\1="' + prefix, footer)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    {head}
    {jsonld.legal(kind, lang, page_title, path)}
</head>
<body>
    <div class="animated-bg" aria-hidden="true"></div>
    <a class="skip-link" href="#main">Skip to content</a>
    {header}

    <main id="main" class="doc">
        <div class="wrap">
            <div class="legal-page">
                <p class="legal-lang"><a href="{other_href}" hreflang="{other_lang}" lang="{other_lang}">{other_label}</a></p>
{body}
            </div>
        </div>
    </main>

    {footer}
</body>
</html>
"""


def replace_region(page, name, content):
    pattern = re.compile(rf"(<!-- build:{name} -->)(.*?)(\s*<!-- /build:{name} -->)", re.S)
    if not pattern.search(page):
        raise SystemExit(f"missing build:{name} marker")
    # Rebuild the closing marker too: keeping the old whitespace added a blank line per run
    # on pages whose region is empty (404).
    body = "\n    " + content if content.strip() else ""
    return pattern.sub(lambda m: m.group(1) + body + "\n    <!-- /build:" + name + " -->", page)


def main():
    for name, (title, description, path) in HAND_PAGES.items():
        file = os.path.join(SITE_DIR, name)
        with open(file, encoding="utf-8") as f:
            page = f.read()
        page = replace_region(page, "head", partials.head(title, description, path, noindex=(name == "404.html")))
        page = replace_region(page, "ld", jsonld.hand(name, page))
        page = replace_region(page, "header", partials.header(name))
        page = replace_region(page, "footer", partials.FOOTER)
        if name == "404.html":
            # Served for any missing path, however deep, so every link must be root-relative.
            page = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)(\./)?', r'\1="/', page)
        with open(file, "w", encoding="utf-8") as f:
            f.write(page)
        print("updated", name)

    for name, (kind, lang, title, description) in LEGAL_PAGES.items():
        with open(os.path.join(SITE_DIR, name), "w", encoding="utf-8") as f:
            f.write(legal_page(kind, lang, title, description, name))
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
