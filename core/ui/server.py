from __future__ import annotations
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from core.preflight.checks import main as preflight_main
from core.policy.guardian import PolicyEngine

app = FastAPI(title="WilsonsRaider UI", version="0.1")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/preflight")
def preflight():
    # Reuse function by capturing stdout would be complex; replicate basic checks instead
    from core.preflight.checks import deps, vault_status
    # Not directly importable; quick re-eval: we expose minimal live info
    return JSONResponse({"message": "Run scripts/preflight.sh for full report"})

@app.get("/policy")
def policy():
    g = PolicyEngine()
    return g.config
