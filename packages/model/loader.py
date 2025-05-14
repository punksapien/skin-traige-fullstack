import io
import os
import torch
import torch.nn as nn
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional
from torchvision.models import efficientnet_b0

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

    try:
        # Try loading the model directly first
        state_dict = torch.load(model_path, map_location=torch.device('cpu'))

        # If it's a state_dict (OrderedDict), load it into our model
        if isinstance(state_dict, dict):
            # Create a proper EfficientNet model
            _model = efficientnet_b0(pretrained=False)
            # Replace the classifier to match our 2-class output
            _model.classifier[1] = nn.Linear(_model.classifier[1].in_features, 2)

            # Adapt the state dict if needed
            adapted_state_dict = {}
            for key, value in state_dict.items():
                if key.startswith('module.'):
                    adapted_state_dict[key[7:]] = value
                else:
                    adapted_state_dict[key] = value

            # Load the adapted state dict into the model
            _model.load_state_dict(adapted_state_dict)

            # Set to evaluation mode
            _model.eval()
        else:
            # It's already a model object
            _model = state_dict

    except Exception as e:
        raise Exception(f"Error loading model: {str(e)}")

    return _model

def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess image bytes for model input using torchvision transforms.
    """
    from torchvision import transforms

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
        # Return a default prediction to avoid breaking the API
        return "unknown", 0.5
