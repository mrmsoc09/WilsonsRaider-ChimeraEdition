from __future__ import annotations
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from core.policy.guardian import PolicyEngine
from core.chaining.planner import ChainPlanner
from core.chaining.patterns import load_patterns

app = FastAPI(title="WilsonsRaider UI", version="0.2")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/policy")
def policy():
    g = PolicyEngine()
    return g.config

@app.get("/validation/tactics")
def validation_tactics():
    g = PolicyEngine()
    profs = g.config.get("validation", {}).get("tactics", {})
    return {"profiles": profs, "redundancy": g.validation_redundancy()}

@app.post("/chains/suggest")
def chains_suggest(artifacts: List[Dict[str, Any]]):
    planner = ChainPlanner()
    # naive mapping for demo: add expected fields if missing
    norm = []
    for a in artifacts:
        a.setdefault("likelihood", 0.3)
        a.setdefault("impact", 0.6)
        a.setdefault("cost", 1.0)
        a.setdefault("proposed_action", "enumerate")
        norm.append(a)
    suggestions = planner.suggest_next(norm)
    return {"suggestions": suggestions, "patterns": load_patterns()}

@app.get("/preflight")
def preflight_info():
    return JSONResponse({"message": "Run scripts/preflight.sh for full environment and OPSEC report"})
