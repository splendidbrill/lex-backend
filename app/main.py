from fastapi import FastAPI

from .routers.chat import router as chat_router

app = FastAPI(title="FastCrew")

# Routers
app.include_router(chat_router)


@app.get("/")
def health() -> dict:
    return {"status": "ok"}

