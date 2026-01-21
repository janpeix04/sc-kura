from fastapi import FastAPI
from app.api.main import router

app = FastAPI(title="SC-Kura", description="SC-Kura API", version="0.0.1")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
