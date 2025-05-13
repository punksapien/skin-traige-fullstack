# Skin Triage Model

A PyTorch model for classifying skin conditions (acne vs other).

## Usage

```python
from skin_triage_model.loader import load_model, predict

# Load the model
model = load_model()

# Make a prediction (with image bytes)
label, confidence = predict(image_bytes)
```

The model returns a label ("acne" or "other") and a confidence score (0-1).
