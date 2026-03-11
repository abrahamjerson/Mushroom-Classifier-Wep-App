from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routes import router
from app.model_loader import load_model_and_artifacts


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading model and artifacts...")
    app.state.artifacts = load_model_and_artifacts()
    print("Model loaded successfully.")
    yield


app = FastAPI(
    title="Mushroom Classifier API",
    description="FastAPI backend for mushroom image classification using ConvNeXt V2.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)