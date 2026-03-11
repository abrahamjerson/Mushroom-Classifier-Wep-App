from fastapi import APIRouter, File, HTTPException, UploadFile, Request

from app.inference import read_image_from_bytes, predict_image
from app.schemas import PredictionResponse, HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
def health_check(request: Request):
    artifacts = request.app.state.artifacts
    config = artifacts["config"]

    return HealthResponse(
        message="Mushroom classifier API is running",
        model_name=config["model_name"],
        num_classes=config["num_classes"],
        others_threshold=config.get("others_threshold", 0.10),
    )


@router.get("/classes")
def get_classes(request: Request):
    artifacts = request.app.state.artifacts
    class_names = artifacts["class_names"]

    return {
        "num_classes": len(class_names),
        "classes": class_names
    }


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: Request, file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    try:
        artifacts = request.app.state.artifacts

        model = artifacts["model"]
        device = artifacts["device"]
        class_names = artifacts["class_names"]
        config = artifacts["config"]

        image_size = config["image_size"]
        mean = config["normalization"]["mean"]
        std = config["normalization"]["std"]
        others_threshold = config.get("others_threshold", 0.10)

        image_bytes = await file.read()
        image = read_image_from_bytes(image_bytes)

        result = predict_image(
            image=image,
            model=model,
            class_names=class_names,
            device=device,
            image_size=image_size,
            mean=mean,
            std=std,
            others_threshold=others_threshold,
            top_k=3,
        )

        return PredictionResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")