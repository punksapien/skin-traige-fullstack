import io
import os
import torch
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional
import torchvision.models as models
from torchvision import transforms

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

    # Create a new EfficientNet model
    # Using efficientnet_b0 as the base model with 2 output classes (acne or other)
    _model = models.efficientnet_b0(weights=None)

    # Modify the classifier to have 2 output classes
    num_features = _model.classifier[1].in_features
    _model.classifier[1] = torch.nn.Linear(num_features, 2)

    # Load the state dictionary
    state_dict = torch.load(model_path, map_location=torch.device('cpu'))

    # If it's just a state_dict, load it directly
    if isinstance(state_dict, dict):
        try:
            _model.load_state_dict(state_dict)
        except Exception as e:
            print(f"Error loading state dict: {e}")
            # If it fails, try loading as is (might be the entire model)
            _model = state_dict
    else:
        # If it's already a model, use it directly
        _model = state_dict

    # Ensure the model is in evaluation mode
    try:
        _model.eval()
    except Exception as e:
        print(f"Warning: Could not set model to eval mode: {e}")
        # If this fails, the model might be in a different format
        # Continue anyway and hope for the best

    return _model

def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess image bytes for model input using torchvision transforms.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),  # auto converts [H, W, C] → [C, H, W] and scales to [0, 1]
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    image_tensor = transform(image).unsqueeze(0)  # [1, 3, 224, 224]
    return image_tensor

def predict(image_bytes: bytes) -> Tuple[str, float]:
    """
    Make a prediction using the model.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Tuple of (label, confidence) where label is "acne" or "other"
    """
    try:
        # Load model if not already loaded
        model = load_model()

        # Preprocess image
        image_tensor = preprocess_image(image_bytes)

        # Make prediction
        with torch.no_grad():
            output = model(image_tensor)

            # Multi-class softmax output
            probabilities = torch.nn.functional.softmax(output, dim=1)[0]
            confidence_value, predicted = torch.max(probabilities, 0)

            label = "acne" if predicted.item() == 1 else "other"

            # Print debug info for troubleshooting
            print(f"Debug: Output shape: {output.shape}, Pred index: {predicted.item()}, Confidence: {confidence_value.item():.4f}")

            return label, confidence_value.item()
    except Exception as e:
        import traceback
        print(f"Error in predict function: {str(e)}")
        print(traceback.format_exc())  # Print the full traceback for debugging
        return "unknown", 0.5
