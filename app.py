import base64, io, pathlib, re, sys, requests
from PIL import Image

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llava:7b"  # try llava:7b-q4_0 for extra speed

def load_and_downscale(image_path: str, max_side: int = 512) -> bytes:
    """Downscale for lower latency; 384–512 is a good sweet spot."""
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / float(max(w, h))
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92, optimize=True)
    return buf.getvalue()

def tidy(text: str) -> str:
    # strip any role prefixes and keep a single short sentence (≤12 words)
    text = re.sub(r"^\s*(Assistant:|<\|assistant\|>)\s*", "", text).strip()
    text = text.splitlines()[0]
    words = [w.strip('"\',') for w in text.split()]
    return (" ".join(words[:12]).rstrip(".") + ".") if words else "No caption."

def caption(path: str) -> str:
    img_bytes = load_and_downscale(path, max_side=512)
    img_b64 = base64.b64encode(img_bytes).decode()

    payload = {
        "model": MODEL,
        "prompt": "Return one short sentence (<=12 words) describing the central object.",
        "images": [img_b64],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 32   # keep token budget tiny for speed
        }
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return tidy(r.json().get("response", ""))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py path/to/image.jpg")
        sys.exit(1)
    print(caption(sys.argv[1]))