from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router
from app.model_loader import load_model_and_artifacts


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading model and artifacts...")
    app.state.artifacts = load_model_and_artifacts()

    config = app.state.artifacts["config"]
    print("Model loaded successfully.")
    print("Model name:", config["model_name"])
    print("Num classes:", config["num_classes"])
    print("Others threshold:", config.get("others_threshold", 0.10))

    yield


app = FastAPI(
    title="Mushroom Classifier API",
    description="FastAPI backend for mushroom image classification using ConvNeXt V2.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)