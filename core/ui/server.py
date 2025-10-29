from __future__ import annotations
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from core.util.env import *  # load .env
from core.policy.guardian import PolicyEngine
from core.chaining.planner import ChainPlanner
from core.chaining.patterns import load_patterns
from core.learning.tracker import LearningTracker

app = FastAPI(title="WilsonsRaider UI", version="0.3")

g = PolicyEngine()
lt = LearningTracker()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/policy")
def policy():
    return g.config

@app.get("/validation/tactics")
def validation_tactics():
    profs = g.config.get("validation", {}).get("tactics", {})
    return {"profiles": profs, "redundancy": g.validation_redundancy()}

@app.post("/chains/suggest")
def chains_suggest(artifacts: List[Dict[str, Any]]):
    planner = ChainPlanner(use_learning=True)
    norm = []
    for a in artifacts:
        a.setdefault("likelihood", 0.3)
        a.setdefault("impact", 0.6)
        a.setdefault("cost", 1.0)
        a.setdefault("proposed_action", "enumerate")
        norm.append(a)
    suggestions = planner.suggest_next(norm)
    return {"suggestions": suggestions, "patterns": load_patterns()}

@app.post("/learning/outcome")
def learning_outcome(event: Dict[str, Any]):
    # event: {asset_type, tactic, success(bool), reward(optional)}
    asset_type = str(event.get("asset_type", "misc"))
    tactic = str(event.get("tactic", "unknown"))
    success = bool(event.get("success", False))
    reward = event.get("reward", None)
    lt.record(asset_type, tactic, success, reward)
    return {"status": "ok"}

@app.get("/learning/recommend")
def learning_recommend(asset_type: str, profile: str = "safe"):
    tactics = g.config.get("validation", {}).get("tactics", {}).get(profile, [])
    ranked = lt.recommend(asset_type, tactics)
    return {"asset_type": asset_type, "profile": profile, "ranked_tactics": ranked}

@app.get("/preflight")
def preflight_info():
    return JSONResponse({"message": "Run scripts/preflight.sh for full environment and OPSEC report"})
