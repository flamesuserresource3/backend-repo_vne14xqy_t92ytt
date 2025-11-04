import os
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Project, Message

app = FastAPI(title="Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(doc)
    if d.get("_id") is not None:
        d["id"] = str(d.pop("_id"))
    # Convert datetime fields to isoformat if present
    for key in ("created_at", "updated_at"):
        if key in d and hasattr(d[key], "isoformat"):
            d[key] = d[key].isoformat()
    return d


@app.get("/")
def read_root():
    return {"message": "Portfolio API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Portfolio endpoints
@app.get("/projects", response_model=List[Project])
def list_projects():
    """Return all projects. If none exist, seed a few defaults on first call."""
    try:
        docs = get_documents("project")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not docs:
        seed: List[Project] = [
            Project(
                title="Interactive 3D Landing",
                description="Playful WebGL landing with Spline and smooth transitions.",
                tags=["React", "Spline", "Framer Motion"],
                link="#",
                repo="#",
            ),
            Project(
                title="Realtime Chat App",
                description="Live chat with presence, emojis, and reactions.",
                tags=["FastAPI", "WebSockets", "MongoDB"],
                link="#",
                repo="#",
            ),
            Project(
                title="Portfolio CMS",
                description="Markdown-powered personal site with SEO.",
                tags=["React", "FastAPI", "Tailwind"],
                link="#",
                repo="#",
            ),
        ]
        for p in seed:
            create_document("project", p)
        docs = get_documents("project")

    return [Project(**serialize_doc(d)) for d in docs]


@app.post("/contact")
def submit_message(payload: Message):
    """Store a contact message."""
    try:
        inserted_id = create_document("message", payload)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Optional: expose schemas for tools that introspect
class SchemaInfo(BaseModel):
    name: str
    fields: Dict[str, str]


@app.get("/schema")
def get_schema():
    return {
        "project": {
            "title": "str",
            "description": "str",
            "tags": "List[str]",
            "link": "Optional[str]",
            "repo": "Optional[str]",
            "thumbnail": "Optional[str]",
        },
        "message": {
            "name": "str",
            "email": "EmailStr",
            "message": "str",
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
