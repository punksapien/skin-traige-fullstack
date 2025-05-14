import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import './ImageUploader.css';
import { API_URL } from '../config';

// Define the prediction response type
interface PredictionResponse {
  label: string;
  confidence: number;
  processing_time_ms?: number;
}

const ImageUploader: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Handle file drop
  const onDrop = useCallback((acceptedFiles: File[]) => {
    setError(null);
    setPrediction(null);

    if (acceptedFiles.length === 0) {
      return;
    }

    const selectedFile = acceptedFiles[0];

    // Only accept image files
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please upload an image file');
      return;
    }

    setFile(selectedFile);

    // Create a preview URL
    const previewUrl = URL.createObjectURL(selectedFile);
    setPreview(previewUrl);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': []
    },
    multiple: false
  });

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError('Please select an image to upload');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create form data for the API request
      const formData = new FormData();
      formData.append('file', file);

      // Make the API request
      const response = await axios.post<PredictionResponse>(
        `${API_URL}/triage-image`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setPrediction(response.data);
    } catch (err: any) {
      console.error('Error uploading image:', err);
      if (err.response) {
        console.error('Error response data:', err.response.data);
        // Show backend error if available
        if (err.response.data && err.response.data.error) {
          setError(`Backend error: ${err.response.data.error}`);
        } else {
          setError('Failed to analyze image. Please try again.');
        }
      } else {
        setError('Failed to analyze image. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Format confidence as percentage
  const formatConfidence = (confidence: number) => {
    return `${(confidence * 100).toFixed(2)}%`;
  };

  return (
    <div className="image-uploader">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        {
          isDragActive ?
            <p>Drop the image here...</p> :
            <p>Drag and drop an image here, or click to select a file</p>
        }
      </div>

      {preview && (
        <div className="preview-container">
          <h3>Selected Image</h3>
          <img
            src={preview}
            alt="Preview"
            className="image-preview"
          />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="analyze-button"
          >
            {loading ? 'Analyzing...' : 'Analyze Image'}
          </button>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {prediction && (
        <div className="prediction-result">
          <h3>Prediction Result</h3>
          <div className="result-item">
            <span className="label">Classification:</span>
            <span className="value">{prediction.label}</span>
          </div>
          <div className="result-item">
            <span className="label">Confidence:</span>
            <span className="value">{formatConfidence(prediction.confidence)}</span>
          </div>
          <div className="result-item">
            <span className="label">Processing Time:</span>
            <span className="value">{prediction.processing_time_ms} ms</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
