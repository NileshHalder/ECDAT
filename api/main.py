"""
FastAPI app entrypoint. Run with: uvicorn api.main:app --reload
"""
from fastapi import FastAPI

from . import db
from .routes import router

app = FastAPI(title="ECDAT API", version="0.1.0")

db.init_db()
app.include_router(router)
