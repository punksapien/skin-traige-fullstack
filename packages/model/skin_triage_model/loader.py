import io
import os
import torch
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional

# Global variable to store loaded model
_model = None

def load_model() -> torch.nn.Module:
    """
    Load the EfficientNet model from the package's model.pth file.
    Returns the loaded PyTorch model.
    """
    global _model

    if _model is not None:
        return _model

    # Get the path to the model file relative to this package
    model_path = Path(__file__).parent.parent / "model.pth"

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {model_path}")

    # Load the model
    _model = torch.load(model_path, map_location=torch.device('cpu'))
    _model.eval()  # Set to evaluation mode

    return _model

def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess image bytes for model input.
    """
    # Open image from bytes
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

    # Resize to expected dimensions (assuming 224x224 for EfficientNet)
    image = image.resize((224, 224))

    # Convert to tensor and normalize
    # Normalization values for ImageNet (commonly used with EfficientNet)
    normalize = lambda x: (x / 255.0 - 0.5) / 0.5
    image_tensor = torch.tensor(normalize(list(image.getdata()))).reshape(3, 224, 224)

    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)

    return image_tensor

def predict(image_bytes: bytes) -> Tuple[str, float]:
    """
    Make a prediction using the model.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Tuple of (label, confidence) where label is "acne" or "other"
    """
    # Load model if not already loaded
    model = load_model()

    # Preprocess image
    image_tensor = preprocess_image(image_bytes)

    # Make prediction
    with torch.no_grad():
        output = model(image_tensor)

    # Get prediction (assuming binary classification)
    probabilities = torch.nn.functional.softmax(output, dim=1)
    confidence, predicted = torch.max(probabilities, 1)

    # Map index to label
    label = "acne" if predicted.item() == 1 else "other"

    return label, confidence.item()
