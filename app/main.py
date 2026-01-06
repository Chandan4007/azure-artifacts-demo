from fastapi import FastAPI
from app.api import router

app = FastAPI(title="FastAPI + Azure Artifacts Demo")

app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok"}
