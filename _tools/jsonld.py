"""JSON-LD blocks, built from what each page really says. No ratings: the App Store shows none yet."""
import html
import json
import re

SITE = "https://shelfreadyapp.com"
APP_STORE = "https://apps.apple.com/app/id6818769240"
ORG = {"@type": "Organization", "name": "Visto Apps", "url": "https://vistoapps.com",
       "founder": {"@type": "Person", "name": "Darius Cirjan"}}
SCREENS = ["phone-new", "phone-result", "phone-batch", "phone-gallery"]


def block(*objs):
    body = ",\n".join(json.dumps(o, ensure_ascii=False, indent=2) for o in objs)
    return '<script type="application/ld+json">\n' + body + "\n    </script>"


def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate(items, 1)]}


def text(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip()


def hand(name, page):
    if name == "index.html":
        app = {
            "@context": "https://schema.org", "@type": "MobileApplication",
            "name": "ShelfReady: Product Photos", "alternateName": "ShelfReady",
            "description": "Take a photo of something you are selling. ShelfReady removes the background on your iPhone and sets the item on a clean studio backdrop with a soft shadow, sized for your listing.",
            "url": SITE + "/", "applicationCategory": "PhotographyApplication", "operatingSystem": "iOS 18.0 or later",
            "inLanguage": "en", "image": SITE + "/img/app-icon-256.png",
            "screenshot": [f"{SITE}/img/{n}.webp" for n in SCREENS],
            "downloadUrl": APP_STORE, "installUrl": APP_STORE,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "url": APP_STORE},
            "author": ORG, "publisher": ORG,
        }
        site = {"@context": "https://schema.org", "@type": "WebSite", "name": "ShelfReady", "url": SITE + "/",
                "inLanguage": "en", "publisher": ORG}
        return block(app, site)
    if name == "support.html":
        faq = []
        for m in re.finditer(r"<details[^>]*>\s*<summary>(.*?)</summary>\s*<div>(.*?)</div>\s*</details>", page, re.S):
            faq.append({"@type": "Question", "name": text(m.group(1)),
                        "acceptedAnswer": {"@type": "Answer", "text": text(m.group(2))}})
        return block({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq},
                     crumbs([("ShelfReady", SITE + "/"), ("Support", SITE + "/support.html")]))
    return ""


def legal(kind, lang, title, path):
    home = SITE + ("/ro/" if False else "/")
    label = title.split(" | ")[0]
    return block(crumbs([("ShelfReady", SITE + "/"), (label, f"{SITE}/{path}")]))
