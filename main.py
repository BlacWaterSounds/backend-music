from fastapi import FastAPI, Header, HTTPException, Depends
from db import SessionLocal, engine
from models import Base, Prompt
import uuid
import os

app = FastAPI()

# Load API key from Railway environment variables
API_KEY = os.getenv("API_KEY")

# Create database tables on startup
Base.metadata.create_all(bind=engine)


# --- AUTH ---
# Used as a FastAPI dependency now instead of a manually-called function,
# so every route gets it identically and none can accidentally skip it.
def verify_key(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]
    if not API_KEY or token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


# --- DB SESSION ---
# Dependency that guarantees the session is closed after each request,
# even if the handler raises. The old code opened a session with
# SessionLocal() in each route and never closed it — under real traffic
# this leaks connections until Postgres runs out and every request
# starts failing with connection errors.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- ROOT + HEALTH ---
# A root route means hitting the bare Railway URL returns something
# meaningful instead of FastAPI's default 404, which is useful for a
# quick "is this even the right service" sanity check.
@app.get("/")
def root():
    return {"status": "ok", "service": "backend-music"}


@app.get("/health")
def health():
    return {"status": "ok"}


# --- GENERATE PROMPT ---
# Lovable sends: { user_id, inputs: { genre, mood, tempo, ... }, mode }
# The old code read `data.get("genre")` at the top level, but genre (and
# every other field) actually lives inside `inputs`. That's the bug that
# made every response say "genre: unknown" no matter what was typed.
@app.post("/generate-prompt")
def generate_prompt(data: dict, authorization: str = Depends(verify_key)):
    inputs = data.get("inputs") or {}

    genre = inputs.get("genre", "unknown")
    mood = inputs.get("mood")
    tempo = inputs.get("tempo")
    style = inputs.get("style")
    keywords = inputs.get("keywords")

    parts = [f"genre: {genre}"]
    if mood:
        parts.append(f"mood: {mood}")
    if tempo:
        parts.append(f"tempo: {tempo}")
    if style:
        parts.append(f"style: {style}")
    if keywords:
        # keywords may arrive as a list or a plain string — handle both
        if isinstance(keywords, list):
            parts.append(f"keywords: {', '.join(str(k) for k in keywords)}")
        else:
            parts.append(f"keywords: {keywords}")

    prompt = "Generated prompt — " + ", ".join(parts)

    return {"prompt": prompt, "meta": {"inputs_received": inputs}}


# --- SAVE PROMPT ---
@app.post("/save-prompt")
def save_prompt(data: dict, authorization: str = Depends(verify_key), db=Depends(get_db)):
    if "user_id" not in data or "prompt" not in data:
        raise HTTPException(status_code=422, detail="user_id and prompt are required")

    new_id = str(uuid.uuid4())
    new_prompt = Prompt(
        id=new_id,
        user_id=data["user_id"],
        prompt=data["prompt"],
    )

    db.add(new_prompt)
    db.commit()

    return {"id": new_id}


# --- LIST PROMPTS ---
@app.get("/prompts/{user_id}")
def get_prompts(user_id: str, authorization: str = Depends(verify_key), db=Depends(get_db)):
    rows = db.query(Prompt).filter(Prompt.user_id == user_id).all()

    return {
        "prompts": [
            {
                "id": r.id,
                "prompt": r.prompt,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    }


# --- SUNO GENERATE ---
# Still a placeholder — this does not call the real Suno API yet.
# Wire this up when you're ready to actually generate audio.
@app.post("/suno/generate")
def suno_generate(data: dict, authorization: str = Depends(verify_key)):
    return {"job_id": str(uuid.uuid4()), "status": "queued"}


# --- UDIO GENERATE ---
# Still a placeholder — same as above, for Udio.
@app.post("/udio/generate")
def udio_generate(data: dict, authorization: str = Depends(verify_key)):
    return {"job_id": str(uuid.uuid4()), "status": "queued"}

