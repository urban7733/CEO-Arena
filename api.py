"""
CEO Arena - FastAPI Backend
Serves the RAG query engine via REST API.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from enum import Enum

from rag.query_engine import CEOQueryEngine

app = FastAPI(title="CEO Arena API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Initialize engine once at startup
engine: CEOQueryEngine | None = None


class Speaker(str, Enum):
    elon_musk = "elon_musk"
    sam_altman = "sam_altman"
    dario_amodei = "dario_amodei"
    mark_zuckerberg = "mark_zuckerberg"


class ChatRequest(BaseModel):
    speaker: Speaker
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    speaker: str
    speaker_name: str
    message: str


class DebateRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    speakers: list[Speaker] | None = None


DISPLAY_NAMES = {
    "elon_musk": "Elon Musk",
    "sam_altman": "Sam Altman",
    "dario_amodei": "Dario Amodei",
    "mark_zuckerberg": "Mark Zuckerberg",
}


@app.on_event("startup")
async def startup():
    global engine
    print("Loading CEO Arena engine...")
    engine = CEOQueryEngine()
    print("Engine ready!")


@app.get("/api/health")
async def health():
    return {"status": "ok", "engine_loaded": engine is not None}


@app.get("/api/speakers")
async def get_speakers():
    return [
        {"id": "elon_musk", "name": "Elon Musk", "company": "Tesla, SpaceX, xAI", "emoji": "🚀"},
        {"id": "sam_altman", "name": "Sam Altman", "company": "OpenAI", "emoji": "🧠"},
        {"id": "dario_amodei", "name": "Dario Amodei", "company": "Anthropic", "emoji": "🛡️"},
        {"id": "mark_zuckerberg", "name": "Mark Zuckerberg", "company": "Meta", "emoji": "👓"},
    ]


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not loaded")

    try:
        response = engine.query(req.speaker.value, req.message)
        return ChatResponse(
            speaker=req.speaker.value,
            speaker_name=DISPLAY_NAMES[req.speaker.value],
            message=response,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/debate")
async def debate(req: DebateRequest):
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not loaded")

    speakers = [s.value for s in req.speakers] if req.speakers else list(DISPLAY_NAMES.keys())

    try:
        responses = engine.debate(req.message, speakers)
        return [
            ChatResponse(
                speaker=speaker,
                speaker_name=DISPLAY_NAMES[speaker],
                message=msg,
            )
            for speaker, msg in responses.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
