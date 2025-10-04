import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from ollama_client import caption_image

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True,
)

@app.post("/caption", response_class=PlainTextResponse)
async def caption(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        text, _ = await asyncio.to_thread(caption_image, img_bytes)
        return text  # just plain text!
    except Exception as e:
        raise HTTPException(400, f"Failed: {e}")

@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"
