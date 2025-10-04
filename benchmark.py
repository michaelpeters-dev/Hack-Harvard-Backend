import base64, io, pathlib, re, sys, time, requests
from PIL import Image

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llava:7b"

def load_and_downscale(image_path: str, max_side: int = 512) -> bytes:
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / float(max(w, h))
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92, optimize=True)
    return buf.getvalue()

def tidy(text: str) -> str:
    text = re.sub(r"^\s*(Assistant:|<\|assistant\|>)\s*", "", text).strip()
    text = text.splitlines()[0]
    words = [w.strip('"\',') for w in text.split()]
    return (" ".join(words[:12]).rstrip(".") + ".") if words else "No caption."

def caption(path: str) -> str:
    img_bytes = load_and_downscale(path, max_side=512)
    img_b64 = base64.b64encode(img_bytes).decode()

    payload = {
        "model": MODEL,
        "prompt": "Describe the image in one short, concrete caption.",
        "images": [img_b64],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 32
        }
    }

    start = time.perf_counter()
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    elapsed = time.perf_counter() - start
    r.raise_for_status()

    text = tidy(r.json().get("response", ""))
    return text, elapsed

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py path/to/image.jpg")
        sys.exit(1)

    caption_text, seconds = caption(sys.argv[1])
    print(f"Caption: {caption_text}")
    print(f"Time taken: {seconds:.2f} seconds")
