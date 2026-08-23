import os
import sys

# Make the project root importable when this module is loaded as
# backend.main (uvicorn backend.main:app) rather than run as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import report

app = FastAPI(title="Business Report Generator API")

# Dev convenience: allow the Vite dev server's origin directly (useful if
# you run frontend and backend as separate `npm run dev` / `uvicorn`
# processes without the Vite proxy). Tighten this to your real domain(s)
# before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
