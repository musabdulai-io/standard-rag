# backend/app/main.py
"""
FastAPI application entry point for Standard RAG.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import close_db
from app.core.exceptions import AppException
from app.core.observability import logs
from app.core.pinecone import get_pinecone_store


async def _try_seed():
    """Attempt to seed sample documents. Skips gracefully if tables don't exist."""
    try:
        from sqlalchemy import text
        from app.core.database import async_session_factory

        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM documents WHERE is_sample = true")
            )
            if result.scalar() == 0:
                logs.info("Seeding sample documents...", "main")
                from scripts.seed import seed_documents
                await seed_documents()
    except Exception as e:
        logs.warning(f"Seed skipped (tables may not exist yet): {e}", "main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logs.info("Starting application", "main")

    # Initialize Pinecone
    pinecone = await get_pinecone_store()

    # Try to seed (skips if tables don't exist yet)
    await _try_seed()

    logs.info("Services initialized", "main")

    yield

    # Cleanup
    await close_db()
    await pinecone.close()
    logs.info("Application shutdown complete", "main")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS middleware
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions."""
    logs.error(
        exc.message,
        "exception",
        metadata={"status_code": exc.status_code, **exc.details},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
        },
    )


@app.get("/healthcheck")
async def healthcheck():
    """Simple healthcheck for Cloud Run startup probe."""
    return {"status": "ok"}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    pinecone = await get_pinecone_store()
    pinecone_healthy = await pinecone.health_check()

    return {
        "status": "healthy" if pinecone_healthy else "degraded",
        "services": {
            "pinecone": "healthy" if pinecone_healthy else "unhealthy",
        },
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# Import and include routers
from app.features.rag.routes import router as rag_router

app.include_router(rag_router, prefix=settings.API_PREFIX)
