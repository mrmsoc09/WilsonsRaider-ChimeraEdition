from fastapi import FastAPI
from pydantic import BaseModel
import os, time

app = FastAPI(title="WilsonsRaider-ChimeraEdition UI", version="0.1.0")

class Health(BaseModel):
    status: str
    time: float

@app.get("/health", response_model=Health)
def health():
    return Health(status="ok", time=time.time())

@app.get("/")
def root():
    return {"name": "WilsonsRaider-ChimeraEdition", "ui": "ok"}
