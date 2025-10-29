from __future__ import annotations
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from core.policy.guardian import PolicyEngine

app = FastAPI(title="WilsonsRaider UI", version="0.1")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/preflight")
def preflight():
    # For full details, run scripts/preflight.sh
    return JSONResponse({"message": "Run scripts/preflight.sh for full environment and OPSEC report"})

@app.get("/policy")
def policy():
    g = PolicyEngine()
    return g.config
