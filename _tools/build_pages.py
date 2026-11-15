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

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGAL_DIR = os.path.join(SITE_DIR, "_tools", "legal")

HAND_PAGES = {
    "index.html": (
        "ShelfReady: product photos for people who sell their things",
        "Take a photo of something you are selling. ShelfReady lifts it off whatever it was lying "
        "on and sets it on a clean backdrop with a soft shadow, sized for your listing. On your "
        "iPhone, with nothing uploaded.",
        "",
    ),
    "support.html": (
        "Support | ShelfReady",
        "Help with ShelfReady: removing backgrounds, fixing a cutout, free saves, restoring "
        "purchases, managing your subscription, deleting photos and privacy choices.",
        "support.html",
    ),
    "404.html": (
        "Page not found | ShelfReady",
        "This page is not on shelfreadyapp.com.",
        "404.html",
    ),
}

LEGAL_PAGES = {
    "privacy.html": ("privacy", "en", "Privacy Policy | ShelfReady",
                     "How ShelfReady handles your data. Your photos are edited on your device and never uploaded."),
    "terms.html": ("terms", "en", "Terms of Use | ShelfReady",
                   "The terms for using ShelfReady, including free saves, subscriptions and the lifetime purchase."),
    "ro/privacy.html": ("privacy", "ro", "Politica de confidențialitate | ShelfReady",
                        "Cum tratează ShelfReady datele tale. Pozele tale sunt editate pe dispozitiv și nu sunt încărcate nicăieri."),
    "ro/terms.html": ("terms", "ro", "Termeni de utilizare | ShelfReady",
                      "Termenii de utilizare ShelfReady, inclusiv salvările gratuite, abonamentele și achiziția pe viață."),
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
    head = partials.head(page_title, description, path)
    if prefix:
        head = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)', r'\1="' + prefix, head)
        head = head.replace('property="og:locale" content="en_US"', 'property="og:locale" content="ro_RO"')
    header = partials.header()
    footer = partials.FOOTER
    if prefix:
        header = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)(\./)?', r'\1="' + prefix, header)
        footer = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)(\./)?', r'\1="' + prefix, footer)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    {head}
    <link rel="alternate" hreflang="{other_lang}" href="{partials.SITE}/{other_href.replace('../', '')}">
</head>
<body>
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
    return pattern.sub(lambda m: m.group(1) + "\n    " + content + m.group(3), page)


def main():
    for name, (title, description, path) in HAND_PAGES.items():
        file = os.path.join(SITE_DIR, name)
        with open(file, encoding="utf-8") as f:
            page = f.read()
        page = replace_region(page, "head", partials.head(title, description, path))
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
