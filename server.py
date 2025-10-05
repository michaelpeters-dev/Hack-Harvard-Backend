import base64, pathlib
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, HTMLResponse
from ollama_client import caption_image

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Debug info
LATEST = {"jpeg": b"", "prompt": "", "saved": ""}
DESKTOP = pathlib.Path.home() / "Desktop"
DESKTOP.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def status_page():
    if not LATEST["jpeg"]:
        return HTMLResponse("<h2>CaptionServer — Ready</h2><p>POST /caption</p>")
    b64 = base64.b64encode(LATEST["jpeg"]).decode()
    html = f"""
    <h2>CaptionServer — Latest Upload</h2>
    <p><b>Bytes:</b> {len(LATEST['jpeg'])}</p>
    <p><b>Prompt:</b> <code>{LATEST['prompt'] or '(none)'}</code></p>
    <p><b>Saved to:</b> {LATEST['saved']}</p>
    <img src="data:image/jpeg;base64,{b64}" style="max-width:360px;display:block"/>
    <p>POST endpoint: <code>/caption</code></p>
    """
    return HTMLResponse(html)

@app.post("/caption", response_class=PlainTextResponse)
async def caption(req: Request):
    jpeg = await req.body()
    if not jpeg:
        raise HTTPException(400, "Empty body")
    prompt = req.headers.get("x-prompt", "").strip()
    save_path = DESKTOP / "last_roi.jpg"
    save_path.write_bytes(jpeg)
    LATEST.update(jpeg=jpeg, prompt=prompt, saved=str(save_path))
    try:
        text, _elapsed = caption_image(jpeg)
        return PlainTextResponse(text or "Not sure.")
    except Exception as e:
        raise HTTPException(500, f"Caption failed: {e}")