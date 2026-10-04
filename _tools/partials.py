"""Shared header, footer and head tags for every page on shelfreadyapp.com.

build_pages.py writes these into each page between <!-- build:NAME --> markers, so the header
and footer are identical everywhere and change in one place.
"""

SITE = "https://shelfreadyapp.com"
APP_STORE_URL = "https://apps.apple.com/app/id6818769240"
APP_ID = "6818769240"
CONTACT = "iosallapps@icloud.com"
DEVELOPER = "Darius Cirjan"
STYLE_VERSION = "1"

HEADER = """<header class="site-header">
        <div class="container bar">
            <a class="brand" href="./" aria-label="ShelfReady home">
                <img src="img/app-icon-128.webp" width="34" height="34" alt="">
                <span>ShelfReady</span>
            </a>
            <nav aria-label="Main">
                <ul class="nav-links">
                    <li class="nav-hide"><a href="./#how">How it works</a></li>
                    <li class="nav-hide"><a href="./#features">Features</a></li>
                    <li class="nav-hide"><a href="support.html">Support</a></li>
                    <li><a class="nav-cta" href="{app}">Get the app</a></li>
                </ul>
            </nav>
        </div>
    </header>""".format(app=APP_STORE_URL)

FOOTER = """<footer class="site-footer">
        <div class="container">
            <div class="footer-grid">
                <div>
                    <a class="brand" href="./" aria-label="ShelfReady home">
                        <img src="img/app-icon-128.webp" width="34" height="34" alt="">
                        <span>ShelfReady</span>
                    </a>
                    <p>Product photos for sellers, made on your iPhone.<br>
                    Contact: <a href="mailto:{contact}">{contact}</a></p>
                </div>
                <nav aria-label="Footer">
                    <ul class="footer-links">
                        <li><a href="privacy.html">Privacy Policy</a></li>
                        <li><a href="terms.html">Terms of Use</a></li>
                        <li><a href="support.html">Support</a></li>
                        <li><a href="{app}">App Store</a></li>
                    </ul>
                </nav>
            </div>
            <p class="legal-credit">&copy; 2026 {dev}. Apple, the Apple logo, iPhone and App Store are trademarks of Apple Inc., registered in the U.S. and other countries and regions.</p>
        </div>
    </footer>""".format(contact=CONTACT, app=APP_STORE_URL, dev=DEVELOPER)


def head(title, description, path, image_alt="The ShelfReady app icon: a knitted jumper on a stone plinth, half on forest green, half on a cream studio wall."):
    url = SITE + "/" + path
    return f"""<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="apple-itunes-app" content="app-id={APP_ID}">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="theme-color" content="#F1E4D4">
    <link rel="canonical" href="{url}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="ShelfReady">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{SITE}/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="{image_alt}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{SITE}/og-image.png">
    <link rel="icon" href="favicon.ico" sizes="48x48">
    <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="favicon-16.png">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">
    <link rel="preload" href="fonts/newsreader-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="styles.css?v={STYLE_VERSION}">"""
