from fastapi import FastAPI

from app.api.routes import health, items, llm
from app.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(health.router)
app.include_router(items.router)
app.include_router(llm.router)
