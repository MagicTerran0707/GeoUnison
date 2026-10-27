"""Minimal image-chat client; model serving code and weights are not included."""
import argparse
import base64
import io
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image


def image_content(path):
    """Encode a local image as PNG without resizing or changing frame order."""
    buffer = io.BytesIO()
    with Image.open(path) as image:
        image.convert("RGB").save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return {"type": "image_url", "image_url": {"url": "data:image/png;base64," + encoded}}


def predict(endpoint, model, images, prompt, max_tokens=512, timeout=120):
    """Call a user-provided, image-capable chat-completions endpoint."""
    url = urllib.parse.urlsplit(endpoint)
    if url.scheme not in {"http", "https"} or not url.hostname:
        raise ValueError("The endpoint must be an HTTP(S) URL.")
    if url.username or url.password:
        raise ValueError("Use GEOUNISON_API_KEY rather than credentials in the URL.")
    if not images or not prompt.strip() or max_tokens < 1 or timeout <= 0:
        raise ValueError("Images, a nonempty prompt, and positive generation limits are required.")
    content = [image_content(path) for path in images]
    content.append({"type": "text", "text": prompt})
    payload = {"model": model, "messages": [{"role": "user", "content": content}],
               "temperature": 0, "max_tokens": max_tokens, "stream": False}
    headers = {"Content-Type": "application/json"}
    if os.environ.get("GEOUNISON_API_KEY"):
        headers["Authorization"] = "Bearer " + os.environ["GEOUNISON_API_KEY"]
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"),
                                     headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.load(response)
    try:
        answer = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Expected a chat-completions response with message.content.") from exc
    if not isinstance(answer, str):
        raise ValueError("This preview client expects a text response.")
    return answer, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", nargs="+", required=True, type=Path,
                        help="Local image paths, in temporal order when applicable.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--endpoint", required=True,
                        help="Your own image-capable chat-completions URL; no service is bundled.")
    parser.add_argument("--model", default="GeoUnison", help="Model name configured by your server.")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--output", type=Path, help="Optional JSON output; existing files are not overwritten.")
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error("Output already exists; choose another path.")
    try:
        answer, result = predict(args.endpoint, args.model, args.images, args.prompt,
                                 args.max_new_tokens, args.timeout)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
        print(answer)
    except urllib.error.HTTPError as exc:
        print(f"Inference request failed (HTTP {exc.code}). Check your server configuration.", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"Inference failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
