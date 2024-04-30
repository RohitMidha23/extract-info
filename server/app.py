import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from langserve import add_routes

from server.api import extract
from server.extract_info import (
    ExtractRequest,
    ExtractResponse,
    extraction_runnable,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bridge : Extraction",
    description="A service for extracting structured data from text.",
)


ROOT = Path(__file__).parent.parent

ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")

if ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/ready")
def ready() -> str:
    return "ok"


# Include API endpoints for extractor definitions
app.include_router(extract.router)

add_routes(
    app,
    extraction_runnable.with_types(
        input_type=ExtractRequest, output_type=ExtractResponse
    ),
    path="/extract_text",
    enabled_endpoints=["invoke", "batch"],
)


# Serve the frontend
UI_DIR = str(ROOT / "ui")

if os.path.exists(UI_DIR):
    app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")
else:
    logger.warning("No UI directory found, serving API only.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
