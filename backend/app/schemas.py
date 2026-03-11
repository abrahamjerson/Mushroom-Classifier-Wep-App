
from typing import List, Optional
from pydantic import BaseModel


class TopPrediction(BaseModel):
    label: str
    confidence: float


class PredictionResponse(BaseModel):
    predicted_label: str
    confidence: float
    final_prediction: str
    rejection_reason: Optional[str] = None
    top3_predictions: List[TopPrediction]


class HealthResponse(BaseModel):
    message: str
    model_name: str
    num_classes: int
    others_threshold: float