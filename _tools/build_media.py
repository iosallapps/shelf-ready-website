"""Build every image the site uses from the app's own art.

    python3 _tools/build_media.py

Sources: ~/Developer/ShelfReady/StudioApp/Assets.xcassets (the app's bundled botanical art,
sample product photos and the app icon). Outputs land in img/ and at the site root (favicons).
Needs Pillow with WebP.
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ASSETS = os.path.expanduser("~/Developer/ShelfReady/StudioApp/Assets.xcassets")
IMG = os.path.join(SITE, "img")

WEBP_QUALITY = 78
SAMPLES = ["Sneakers", "Bags", "Electronics", "Beauty"]
SAMPLE_WIDTHS = (360, 640)
HERO_WIDTHS = (480, 760)
PAIR_WIDTHS = (360, 600)


def asset(path):
    return Image.open(os.path.join(ASSETS, path)).convert("RGB")


def save_widths(image, name, widths):
    for width in widths:
        height = round(image.height * width / image.width)
        resized = image.resize((width, height), Image.LANCZOS)
        resized.save(os.path.join(IMG, f"{name}-{width}.webp"), "WEBP", quality=WEBP_QUALITY, method=6)
        print(name, width, height)


def main():
    os.makedirs(IMG, exist_ok=True)

    # Hero: the app's own before and after artwork (the icon art, without the icon mask).
    hero = Image.open(os.path.join(ASSETS, "AppIcon.appiconset/appiconstudio 1.png")).convert("RGB")
    save_widths(hero, "hero-split", HERO_WIDTHS)

    # Leaf shadow walls, used behind the hero and the privacy section.
    save_widths(asset("BotanicalStudio.imageset/BotanicalStudio.jpg"), "leaves-cream", (900,))
    save_widths(asset("BotanicalProduct.imageset/BotanicalProduct.jpg"), "leaves-white", (900,))

    # Before and after pair from the welcome screen.
    save_widths(asset("WelcomeHero.imageset/WelcomeHero@3x.png"), "before", PAIR_WIDTHS)
    save_widths(asset("WelcomeHeroAfter.imageset/WelcomeHeroAfter@3x.png"), "after", PAIR_WIDTHS)

    for sample in SAMPLES:
        save_widths(asset(f"Sample{sample}.dataset/Sample{sample}.jpg"), f"sample-{sample.lower()}", SAMPLE_WIDTHS)

    icon = Image.open(os.path.join(ASSETS, "AppIcon.appiconset/appiconstudio 1.png")).convert("RGB")
    for size, name in ((16, "favicon-16.png"), (32, "favicon-32.png"), (180, "apple-touch-icon.png")):
        icon.resize((size, size), Image.LANCZOS).save(os.path.join(SITE, name), optimize=True)
    icon.resize((48, 48), Image.LANCZOS).save(
        os.path.join(SITE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    for size in (128, 256):
        icon.resize((size, size), Image.LANCZOS).save(
            os.path.join(IMG, f"app-icon-{size}.webp"), "WEBP", quality=88, method=6)


if __name__ == "__main__":
    main()
