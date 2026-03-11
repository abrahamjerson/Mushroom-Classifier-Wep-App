
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import torch
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

# Building transforms
def build_inference_transform(image_size: int, mean: list, std: list):
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std)
    ])

# Loading image
def read_image_from_bytes(image_bytes: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        return image
    except (UnidentifiedImageError, OSError, ValueError) as e:
        raise ValueError(f"Invalid image file: {e}")


def predict_image(
    image: Image.Image,
    model: torch.nn.Module,
    class_names: List[str],
    device: torch.device,
    image_size: int,
    mean: list,
    std: list,
    others_threshold: float = 0.05,
    top_k: int = 3,
) -> Dict[str, Any]:
    transform = build_inference_transform(
        image_size=image_size,
        mean=mean,
        std=std
    )

    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(input_tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    top_k = min(top_k, len(class_names))
    top_indices = np.argsort(probs)[::-1][:top_k]

    top_predictions = []
    for idx in top_indices:
        top_predictions.append({
            "label": class_names[idx],
            "confidence": float(probs[idx])
        })

    predicted_idx = int(np.argmax(probs))
    predicted_label = class_names[predicted_idx]
    confidence = float(probs[predicted_idx])

    final_prediction = predicted_label
    rejection_reason = None

    if confidence < others_threshold:
        final_prediction = "others"
        rejection_reason = f"top1_confidence_below_{others_threshold}"

    return {
        "predicted_label": predicted_label,
        "confidence": confidence,
        "final_prediction": final_prediction,
        "rejection_reason": rejection_reason,
        "top3_predictions": top_predictions
    }