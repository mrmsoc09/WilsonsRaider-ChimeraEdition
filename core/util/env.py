from __future__ import annotations
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()  # load variables from .env if present
except Exception:
    pass
