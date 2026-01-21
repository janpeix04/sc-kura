from fastapi import FastAPI

app = FastAPI(title="SC-Kura", description="SC-Kura API", version="0.0.1")


@app.get("/")
def read_root():
    return {"Hello": "World"}
