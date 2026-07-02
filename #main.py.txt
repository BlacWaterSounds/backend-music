#main.py

from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

import os
API_KEY = os.getenv("API_KEY")

def verify_key(auth: str):
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-prompt")
def generate_prompt(data: dict, authorization: str = Header(None)):
    verify_key(authorization)
    # Your logic here
    return {"prompt": "Generated prompt", "meta": {}}


@app.post("/save-prompt")
def save_prompt(data: dict, authorization: str = Header(None)):
    verify_key(authorization)
    # Save logic here
    return {"id": "123"}


@app.get("/prompts/{user_id}")
def get_prompts(user_id: str, authorization: str = Header(None)):
    verify_key(authorization)
    # Fetch logic here
    return {"prompts": []}


@app.post("/suno/generate")
def suno_generate(data: dict, authorization: str = Header(None)):
    verify_key(authorization)
    # Suno logic here
    return {"job_id": "abc", "status": "queued"}


@app.post("/udio/generate")
def udio_generate(data: dict, authorization: str = Header(None)):
    verify_key(authorization)
    # Udio logic here
    return {"job_id": "xyz", "status": "queued"}
