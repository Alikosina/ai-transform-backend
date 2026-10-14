from fastapi import FastAPI

from app.api.routes import health, items, llm, mock, portfolio
from app.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(health.router)
app.include_router(items.router)
app.include_router(llm.router)
app.include_router(mock.router)
app.include_router(portfolio.router)
