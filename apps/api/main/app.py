import io
import time
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from skin_triage_model import load_model, predict

# Create FastAPI app
app = FastAPI(
    title="Skin Triage API",
    description="API for classifying skin conditions",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://0.0.0.0:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files at /static
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        import traceback
        print(f"Error processing image: {e}")
        traceback.print_exc()
        processing_time = int((time.time() - start_time) * 1000)
        # Always return a valid JSON error response
        return JSONResponse(
            status_code=500,
            content={
                "label": "error",
                "confidence": 0.0,
                "processing_time_ms": processing_time,
                "error": f"Error processing image: {str(e)}"
            }
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Serve index.html for root
@app.get("/")
async def serve_root():
    return FileResponse("static/index.html")

# Serve index.html for all other non-API routes (SPA fallback)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str, request: Request):
    # Only serve index.html for non-API, non-static, non-docs routes
    if not (full_path.startswith("triage-image") or full_path.startswith("health") or full_path.startswith("docs") or full_path.startswith("static")):
        return FileResponse("static/index.html")
    return JSONResponse(status_code=404, content={"detail": "Not Found"})
