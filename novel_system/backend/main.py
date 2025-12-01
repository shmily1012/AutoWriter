from fastapi import FastAPI

from novel_system.backend.core.config import get_settings
from novel_system.backend.api import api_router

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(api_router)


@app.get("/ping")
def ping():
    return {"status": "ok"}
