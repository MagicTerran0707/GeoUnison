"""Draw pixel-coordinate boxes and/or a binary mask over a local image."""
import argparse
import json
import math
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def render(image_path, boxes=None, mask_path=None, opacity=0.3, line_width=2):
    if not 0 <= opacity <= 1 or line_width < 1:
        raise ValueError("Opacity must be in [0, 1] and line width must be positive.")
    with Image.open(image_path) as source:
        image = source.convert("RGBA")
    if mask_path:
        with Image.open(mask_path) as source:
            mask = source.convert("L")
        if mask.size != image.size:
            raise ValueError("Mask and image dimensions must match; masks are not silently resized.")
        mask = mask.point(lambda value: 255 if value else 0)
        fill = Image.new("RGBA", image.size, (42, 180, 110, 0))
        fill.putalpha(mask.point(lambda value: round(value * opacity)))
        image = Image.alpha_composite(image, fill)
        contour = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(3)))
        edge = Image.new("RGBA", image.size, (0, 120, 65, 0))
        edge.putalpha(contour)
        image = Image.alpha_composite(image, edge)
    if boxes is not None and not isinstance(boxes, list):
        raise ValueError("Boxes must be a JSON list of objects containing xyxy coordinates.")
    draw = ImageDraw.Draw(image)
    for box in boxes or []:
        xyxy = box.get("xyxy") if isinstance(box, dict) else None
        if not isinstance(xyxy, (list, tuple)) or len(xyxy) != 4:
            raise ValueError("Each box needs four pixel coordinates in xyxy order.")
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in xyxy):
            raise ValueError("Box coordinates must be finite numbers.")
        x0, y0, x1, y1 = xyxy
        if not (0 <= x0 < x1 <= image.width and 0 <= y0 < y1 <= image.height):
            raise ValueError("Boxes must be ordered and within the original image; coordinate scales are not guessed.")
        draw.rectangle(xyxy, outline=(0, 150, 80, 255), width=line_width)
        if box.get("label"):
            draw.text((x0 + 2, y0 + 2), str(box["label"]), fill=(0, 90, 45, 255),
                      stroke_width=1, stroke_fill=(255, 255, 255, 255))
    return image.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--boxes", type=Path, help="JSON list: [{\"xyxy\": [x0,y0,x1,y1], \"label\": \"object\"}].")
    parser.add_argument("--mask", type=Path, help="Same-size binary mask, with zero background and nonzero foreground.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--opacity", type=float, default=0.3)
    parser.add_argument("--line-width", type=int, default=2)
    args = parser.parse_args()
    if not args.boxes and not args.mask:
        parser.error("Provide --boxes, --mask, or both.")
    if args.output.exists():
        parser.error("Output already exists; choose another path.")
    try:
        boxes = json.loads(args.boxes.read_text(encoding="utf-8")) if args.boxes else None
        image = render(args.image, boxes, args.mask, args.opacity, args.line_width)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        image.save(args.output)
        print(f"Saved {args.output}")
    except (OSError, ValueError) as exc:
        print(f"Visualization failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
