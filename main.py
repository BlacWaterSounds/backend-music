from fastapi import FastAPI, Header, HTTPException
from db import SessionLocal, engine
from models import Base, Prompt
import uuid
import os

app = FastAPI()

# Load API key from Railway environment variables
API_KEY = os.getenv("API_KEY")

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# --- AUTH CHECK ---
def verify_key(auth: str):
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


# --- HEALTH CHECK ---
@app.get("/health")
def health():
    return {"status": "ok"}


# --- GENERATE PROMPT ---
@app.post("/generate-prompt")
def generate_prompt(data: dict, authorization: str = Header(None)):
    verify_key(authorization)

    # Placeholder logic — Lovable will send structured data
    prompt = f"Generated prompt for genre: {data.get('genre', 'unknown')}"

    return {"prompt": prompt, "meta": {}}


# --- LIST ALL PROMPTS ---
@app.get("/prompts")
def list_prompts(authorization: str = Header(None)):
    verify_key(authorization)

    db = SessionLocal()
    try:
        rows = db.query(Prompt).order_by(Prompt.created_at.desc()).all()
        return {
            "prompts": [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "prompt": r.prompt,
                    "created_at": r.created_at.isoformat()
                }
                for r in rows
            ]
        }
    finally:
        db.close()


# --- CREATE PROMPT ---
@app.post("/prompts")
def create_prompt(data: dict, authorization: str = Header(None)):
    verify_key(authorization)

    db = SessionLocal()
    try:
        new_id = str(uuid.uuid4())
        new_prompt = Prompt(
            id=new_id,
            user_id=data["user_id"],
            prompt=data["prompt"]
        )
        db.add(new_prompt)
        db.commit()
        db.refresh(new_prompt)
        return {
            "id": new_prompt.id,
            "user_id": new_prompt.user_id,
            "prompt": new_prompt.prompt,
            "created_at": new_prompt.created_at.isoformat()
        }
    finally:
        db.close()


# --- GET PROMPT BY ID ---
@app.get("/prompts/{prompt_id}")
def get_prompt(prompt_id: str, authorization: str = Header(None)):
    verify_key(authorization)

    db = SessionLocal()
    try:
        row = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return {
            "id": row.id,
            "user_id": row.user_id,
            "prompt": row.prompt,
            "created_at": row.created_at.isoformat()
        }
    finally:
        db.close()


# --- SAVE PROMPT (deprecated — use POST /prompts) ---
@app.post("/save-prompt")
def save_prompt(data: dict, authorization: str = Header(None)):
    verify_key(authorization)

    db = SessionLocal()
    try:
        new_id = str(uuid.uuid4())
        new_prompt = Prompt(
            id=new_id,
            user_id=data["user_id"],
            prompt=data["prompt"]
        )
        db.add(new_prompt)
        db.commit()
        return {"id": new_id}
    finally:
        db.close()


# --- LIST PROMPTS BY USER (deprecated — use GET /prompts) ---
@app.get("/prompts/user/{user_id}")
def get_prompts_by_user(user_id: str, authorization: str = Header(None)):
    verify_key(authorization)

    db = SessionLocal()
    try:
        rows = db.query(Prompt).filter(Prompt.user_id == user_id).all()
        return {
            "prompts": [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "prompt": r.prompt,
                    "created_at": r.created_at.isoformat()
                }
                for r in rows
            ]
        }
    finally:
        db.close()



# --- SUNO GENERATE ---
@app.post("/suno/generate")
def suno_generate(data: dict, authorization: str = Header(None)):
    verify_key(authorization)

    # Placeholder — Lovable will wire this to Suno API later
    return {"job_id": str(uuid.uuid4()), "status": "queued"}


# --- UDIO GENERATE ---
@app.post("/udio/generate")
def udio_generate(data: dict, authorization: str = Header(None)):
    verify_key(authorization)

    # Placeholder — Lovable will wire this to Udio API later
    return {"job_id": str(uuid.uuid4()), "status": "queued"}


