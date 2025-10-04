import base64, io, re, time, requests
from PIL import Image

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llava:7b"  # or "llava:7b-q4_0" for speed

def _downscale(img_bytes: bytes, max_side: int = 512) -> bytes:
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        s = max_side / float(max(w, h))
        img = img.resize((int(w*s), int(h*s)), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=92, optimize=True)
    return buf.getvalue()

def _tidy(text: str) -> str:
    text = re.sub(r"^\s*(Assistant:|<\|assistant\|>)\s*", "", text or "").strip()
    text = text.splitlines()[0] if text else ""
    words = [w.strip('"\',') for w in text.split()]
    return (" ".join(words[:12]).rstrip(".") + ".") if words else "No caption."

def caption_image(img_bytes: bytes) -> tuple[str, float]:
    small = _downscale(img_bytes, 512)
    payload = {
        "model": MODEL,
        "prompt": "Describe the image in one short, concrete caption.",
        "images": [base64.b64encode(small).decode()],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 32}
    }
    t0 = time.perf_counter()
    r = requests.post(OLLAMA_URL, json=payload, timeout=120); r.raise_for_status()
    return _tidy(r.json().get("response", "")), time.perf_counter() - t0
