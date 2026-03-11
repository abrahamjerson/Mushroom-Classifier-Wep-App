
from pathlib import Path
import json
import torch
import timm


BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "weights"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

WEIGHTS_PATH = WEIGHTS_DIR / "best_model.pth"
CLASS_NAMES_PATH = ARTIFACTS_DIR / "class_names.json"
CONFIG_PATH = ARTIFACTS_DIR / "inference_config.json"

# For loading json files
def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# For loading class names
def load_class_names():
    if not CLASS_NAMES_PATH.exists():
        raise FileNotFoundError(f"class_names.json not found at: {CLASS_NAMES_PATH}")
    class_names = load_json(CLASS_NAMES_PATH)
    if not isinstance(class_names, list) or len(class_names) == 0:
        raise ValueError("class_names.json must contain a non-empty list.")
    return class_names

# For loading inference config
def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"inference_config.json not found at: {CONFIG_PATH}")
    config = load_json(CONFIG_PATH)
    return config

# For building model
def build_model(model_name: str, num_classes: int, device: torch.device):
    model = timm.create_model(
        model_name,
        pretrained=False,
        num_classes=num_classes
    )
    model = model.to(device)
    return model

# For loading model
def load_model_and_artifacts():
    device = torch.device("cpu")

    class_names = load_class_names()
    config = load_config()

    model_name = config["model_name"]
    num_classes = config["num_classes"]

    if num_classes != len(class_names):
        raise ValueError(
            f"Mismatch: config num_classes={num_classes}, "
            f"but class_names has {len(class_names)} entries."
        )

    if not WEIGHTS_PATH.exists():
        raise FileNotFoundError(f"Model weights not found at: {WEIGHTS_PATH}")

    model = build_model(
        model_name=model_name,
        num_classes=num_classes,
        device=device
    )

    state_dict = torch.load(WEIGHTS_PATH, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()

    return {
        "model": model,
        "device": device,
        "class_names": class_names,
        "config": config,
    }