from __future__ import annotations
import os, sqlite3, time
from typing import List, Dict, Any

DB_PATH = os.getenv("WR_CACHE_DB", "data/cache.db")

class LearningTracker:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with sqlite3.connect(DB_PATH) as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS tactic_stats (
                  asset_type TEXT NOT NULL,
                  tactic TEXT NOT NULL,
                  trials INTEGER NOT NULL DEFAULT 0,
                  success INTEGER NOT NULL DEFAULT 0,
                  reward REAL NOT NULL DEFAULT 0.0,
                  last_ts INTEGER NOT NULL DEFAULT 0,
                  PRIMARY KEY(asset_type, tactic)
                )
                """
            )

    def record(self, asset_type: str, tactic: str, success: bool, reward: float | None = None) -> None:
        r = 1.0 if success else 0.0
        if reward is not None:
            r = reward
        now = int(time.time())
        with sqlite3.connect(DB_PATH) as c:
            row = c.execute(
                "SELECT trials, success, reward FROM tactic_stats WHERE asset_type=? AND tactic=?",
                (asset_type, tactic),
            ).fetchone()
            if row:
                trials, succ, rew = row
                trials += 1
                succ += (1 if success else 0)
                rew += r
                c.execute(
                    "UPDATE tactic_stats SET trials=?, success=?, reward=?, last_ts=? WHERE asset_type=? AND tactic=?",
                    (trials, succ, rew, now, asset_type, tactic),
                )
            else:
                c.execute(
                    "INSERT INTO tactic_stats(asset_type, tactic, trials, success, reward, last_ts) VALUES(?,?,?,?,?,?)",
                    (asset_type, tactic, 1, 1 if success else 0, r, now),
                )

    def recommend(self, asset_type: str, tactics: List[str], epsilon: float = 0.1) -> List[Dict[str, Any]]:
        # Returns tactics ranked by estimated value with epsilon exploration
        with sqlite3.connect(DB_PATH) as c:
            stats = {}
            for t in tactics:
                row = c.execute(
                    "SELECT trials, success, reward FROM tactic_stats WHERE asset_type=? AND tactic=?",
                    (asset_type, t),
                ).fetchone()
                if row:
                    trials, succ, rew = row
                    avg = (rew / trials) if trials else 0.0
                else:
                    trials, succ, rew, avg = 0, 0, 0.0, 0.0
                stats[t] = {"trials": trials, "success": succ, "reward": rew, "avg": avg}
        # epsilon-greedy: add small exploration bias to low-trial tactics
        ranked = []
        for t in tactics:
            s = stats[t]
            explore_bonus = epsilon if s["trials"] < 3 else 0.0
            score = s["avg"] + explore_bonus
            ranked.append({"tactic": t, "score": score, **s})
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked
