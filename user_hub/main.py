# FastAPI backend for User Hub
from fastapi import FastAPI

app = FastAPI()

@app.get("/status")
def status():
    return {"status": "Wilsons-Raiders User Hub running"}
