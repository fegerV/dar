from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.lifespan import lifespan
from app.middleware.request_id import RequestIdMiddleware

app = FastAPI(
    title="DarAgent API",
    version="0.1.0",
    description="AI-сервис персональных видеопоздравлений",
    lifespan=lifespan,
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.api.v1.router import v1_router

app.include_router(v1_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
