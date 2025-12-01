from fastapi import FastAPI

from novel_system.backend.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)


@app.get("/ping")
def ping():
    return {"status": "ok"}
