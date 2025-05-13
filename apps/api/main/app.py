import io
import time
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from skin_triage_model import load_model, predict

# Create FastAPI app
app = FastAPI(
    title="Skin Triage API",
    description="API for classifying skin conditions",
    version="0.1.0"
)

# Response model
class PredictionResponse(BaseModel):
    label: str
    confidence: float
    processing_time_ms: int

@app.on_event("startup")
async def startup_event():
    """Load the model on startup"""
    try:
        load_model()
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        # We don't raise an exception here because we want the API to start
        # even if the model fails to load. The endpoint will handle the error.

@app.post("/triage-image", response_model=PredictionResponse)
async def triage_image(file: UploadFile = File(...)):
    """
    Classify an image as 'acne' or 'other'
    """
    # Check if the file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not an image. Please upload an image file."
        )

    try:
        # Read image bytes
        start_time = time.time()
        contents = await file.read()

        # Get prediction
        label, confidence = predict(contents)

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)  # ms

        # Return prediction
        return PredictionResponse(
            label=label,
            confidence=confidence,
            processing_time_ms=processing_time
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
