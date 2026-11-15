"""Shared header, footer and head tags for every page on shelfreadyapp.com.

build_pages.py writes these into each page between <!-- build:NAME --> markers, so the header
and footer are identical everywhere and change in one place.
"""

SITE = "https://shelfreadyapp.com"
APP_STORE_URL = "https://apps.apple.com/app/id6818769240"
APP_ID = "6818769240"
CONTACT = "iosallapps@gmail.com"
DEVELOPER = "Visto Apps, the brand of Darius Cirjan"
STYLE_VERSION = "20261115"
OG_ALTERNATE = {"privacy.html": ["ro_RO"], "terms.html": ["ro_RO"], "ro/privacy.html": ["en_US"], "ro/terms.html": ["en_US"]}
OG_ALT = ("An amber serum bottle and a cream jar, half on a stone block in leafy light and half on a "
          "clean blush background, next to the words: Take the photo. Skip the studio.")


def header(current=""):
    def link(href, label, extra=""):
        here = ' aria-current="page"' if href == current else ""
        cls = f' class="{extra}"' if extra else ""
        return f'<li{cls}><a href="{href}"{here}>{label}</a></li>'

    return f"""<header class="site-header">
        <div class="wrap">
            <a class="brand" href="./">
                <img src="img/app-icon-64.webp" width="32" height="32" alt="">
                <span>ShelfReady</span>
            </a>
            <nav aria-label="Main">
                <ul class="nav">
                    {link("./#how", "How it works", "nav-wide")}
                    {link("support.html", "Support", "nav-narrow-hide")}
                    <li><a class="nav-app" href="{APP_STORE_URL}">Get the app</a></li>
                </ul>
            </nav>
        </div>
    </header>"""


FOOTER = f"""<footer class="site-footer">
        <div class="wrap">
            <div class="footer-top">
                <div>
                    <a class="brand" href="./">
                        <img src="img/app-icon-64.webp" width="32" height="32" alt="" loading="lazy">
                        <span>ShelfReady</span>
                    </a>
                    <p>For iPhone. Questions or problems: <a href="mailto:{CONTACT}">{CONTACT}</a></p>
                </div>
                <nav aria-label="Footer">
                    <ul class="footer-links">
                        <li><a href="support.html">Support</a></li>
                        <li><a href="privacy.html">Privacy Policy</a></li>
                        <li><a href="terms.html">Terms of Use</a></li>
                        <li><a href="{APP_STORE_URL}">App Store</a></li>
                    </ul>
                </nav>
            </div>
            <p class="footer-note">&copy; 2026 {DEVELOPER}. Apple, the Apple logo, iPhone and App Store are trademarks of Apple Inc., registered in the U.S. and other countries and regions.</p>
            <p class="footer-made"><a href="https://vistoapps.com/apps.html">More apps by Visto Apps</a> &middot; Made by <a href="https://vistoapps.com">Visto Apps</a></p>
        </div>
    </footer>"""


def head(title, description, path, locale="en_US", alternates=None, noindex=False):
    url = SITE + "/" + path
    robots = '<meta name="robots" content="noindex, follow">\n    ' if noindex else ""
    alt_links = "".join(f'\n    <link rel="alternate" hreflang="{l}" href="{SITE}/{h}">' for l, h in (alternates or []))
    alt_locales = "".join(f'\n    <meta property="og:locale:alternate" content="{o}">' for o in (OG_ALTERNATE.get(path) or []))
    return f"""<meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="apple-itunes-app" content="app-id={APP_ID}">
    <meta name="theme-color" content="#130e12">
    <meta name="color-scheme" content="dark">
    {robots}<link rel="canonical" href="{url}">{alt_links}
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="ShelfReady">
    <meta property="og:locale" content="{locale}">{alt_locales}
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{SITE}/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="{OG_ALT}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{SITE}/og-image.png">
    <meta name="twitter:image:alt" content="{OG_ALT}">
    <link rel="icon" href="favicon.ico" sizes="48x48">
    <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="favicon-16.png">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">
    <link rel="preload" href="fonts/instrument-serif.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="styles.css?v={STYLE_VERSION}">"""
