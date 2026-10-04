"""Build every image the site uses from real app output.

    python3 _tools/build_media.py PIPELINE_OUT SCREENS_DIR

PIPELINE_OUT holds the renders written by _tools/render_pipeline.swift: the app's own
StudioPipeline package run on macOS over the sample photos bundled in the app, one file per
photo and background, named "<photo>__<preset id>.bin". SCREENS_DIR holds simulator captures of
the app (c1 result, c3 batch, c5 gallery, c6 new photo). Nothing is retouched: images are only
cropped, resized and re-encoded. One exception, made before the pipeline ran: the maker's name
and logo were painted out of the watch dial in the watches sample, so no brand shows on the site.

Every file is written without EXIF, XMP or any other metadata. Needs Pillow with WebP and AVIF.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
IMG = os.path.join(SITE, "img")
ASSETS = os.path.expanduser("~/Developer/ShelfReady/StudioApp/Assets.xcassets")

QUALITY = {"avif": 58, "webp": 80, "jpg": 82}
STUDIO = ["white-matte", "grey-gloss", "contrast-dark", "warm-glass", "charcoal"]
COLOURS = ["cream", "bone", "blush", "sage", "powder", "sand", "stone", "terracotta", "slate", "navy"]
# The background each category opens on in the app (SellerCategory.presetIdentifier).
CATEGORIES = [
    ("clothing", "white-matte"),
    ("sneakers", "grey-gloss"),
    ("bags", "grey-gloss"),
    ("watches", "charcoal"),
    ("electronics", "contrast-dark"),
    ("beauty", "warm-glass"),
]


def clean(image):
    """A plain RGB copy with no metadata attached."""
    image = image.convert("RGBA")
    flat = Image.new("RGB", image.size, (255, 255, 255))
    flat.paste(image, mask=image.split()[3])
    return Image.frombytes("RGB", flat.size, flat.tobytes())


def save(image, name, widths, formats=("avif", "webp", "jpg")):
    for width in widths:
        height = round(image.height * width / image.width)
        resized = image.resize((width, height), Image.LANCZOS)
        for fmt in formats:
            path = os.path.join(IMG, f"{name}-{width}.{fmt}")
            if fmt == "avif":
                resized.save(path, "AVIF", quality=QUALITY[fmt], speed=4)
            elif fmt == "webp":
                resized.save(path, "WEBP", quality=QUALITY[fmt], method=6)
            else:
                resized.save(path, "JPEG", quality=QUALITY[fmt], optimize=True, progressive=True)
        print(name, width, height)


def subject_box(after, ground_tolerance=18):
    """Bounding box of everything that is not the plain ground, from a render on a flat colour."""
    ground = after.getpixel((4, 4))
    diff = Image.new("L", after.size)
    px, out = after.load(), diff.load()
    for y in range(0, after.height, 2):
        for x in range(0, after.width, 2):
            r, g, b = px[x, y]
            if abs(r - ground[0]) + abs(g - ground[1]) + abs(b - ground[2]) > ground_tolerance:
                out[x, y] = 255
    return diff.getbbox()


def framed(box, size, aspect, padding):
    """A crop of the given aspect (w/h) around box, with padding around the subject, kept inside."""
    left, top, right, bottom = box
    cx, cy = (left + right) / 2, (top + bottom) / 2
    w, h = (right - left) * (1 + padding), (bottom - top) * (1 + padding)
    if w / h > aspect:
        h = w / aspect
    else:
        w = h * aspect
    w, h = min(w, size[0]), min(h, size[1])
    if w / h > aspect:
        w = h * aspect
    else:
        h = w / aspect
    x0 = min(max(cx - w / 2, 0), size[0] - w)
    y0 = min(max(cy - h / 2, 0), size[1] - h)
    return tuple(round(v) for v in (x0, y0, x0 + w, y0 + h))


def main(pipe, screens):
    os.makedirs(IMG, exist_ok=True)

    def render(photo, preset):
        return clean(Image.open(os.path.join(pipe, f"{photo}__{preset}.bin")))

    def original(photo):
        for ext in ("jpg", "png"):
            path = os.path.join(pipe, "..", "in", f"{photo}.{ext}")
            if os.path.exists(path):
                return clean(Image.open(path))
        raise SystemExit(f"no original for {photo}")

    # Hero: the serum and cream jar as photographed on a stone block in leafy light, and the
    # same photo after the app, on Blush. Chosen from every sample on every background at 2x for
    # the most natural contact shadow. Both halves share one crop, so they line up exactly.
    base = render("beauty", "white-matte")
    crop = framed(subject_box(base), base.size, 4 / 5, 0.5)
    save(original("beauty").crop(crop), "hero-before", (480, 768))
    save(render("beauty", "palette-blush").crop(crop), "hero-after", (480, 768))

    # Swatch book: the same headphones on all fifteen backgrounds.
    base = render("electronics", "white-matte")
    crop = framed(subject_box(base), base.size, 1, 0.55)
    for preset in STUDIO + [f"palette-{c}" for c in COLOURS]:
        save(render("electronics", preset).crop(crop), f"swatch-{preset}", (400, 800))

    # Categories: each photo on the background its category opens on, original inset.
    for photo, preset in CATEGORIES:
        out = render(photo, preset)
        light = render(photo, "white-matte")
        crop = framed(subject_box(light), out.size, 1, 0.5)
        save(out.crop(crop), f"cat-{photo}", (420, 700))
        save(original(photo), f"cat-{photo}-before", (260,), formats=("webp", "jpg"))

    # App screens, shown whole.
    for name, label in (("c6", "screen-new"), ("c1", "screen-result"), ("c3", "screen-batch"), ("c5", "screen-gallery")):
        save(clean(Image.open(os.path.join(screens, f"{name}.png"))), label, (360, 640))

    icon = clean(Image.open(os.path.join(ASSETS, "AppIcon.appiconset/appiconstudio 1.png")))
    for size, name in ((16, "favicon-16.png"), (32, "favicon-32.png"), (180, "apple-touch-icon.png")):
        icon.resize((size, size), Image.LANCZOS).save(os.path.join(SITE, name), optimize=True)
    icon.resize((48, 48), Image.LANCZOS).save(os.path.join(SITE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    for size in (64, 128, 256):
        icon.resize((size, size), Image.LANCZOS).save(os.path.join(IMG, f"app-icon-{size}.webp"), "WEBP", quality=88, method=6)
        icon.resize((size, size), Image.LANCZOS).save(os.path.join(IMG, f"app-icon-{size}.png"), optimize=True)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
