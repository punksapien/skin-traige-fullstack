# Skin Triage Microservice

A microservice that accepts images of skin conditions and classifies them as "acne" or "other" using a pre-trained EfficientNet model.

## Project Structure

```
├── apps
│   ├── api            # FastAPI backend
│   └── web            # React frontend (for future)
├── packages
│   └── model          # PyTorch model and loading utilities
├── Dockerfile
├── docker-compose.yml
├── fly.toml
└── turbo.json
```

## Requirements

- Docker
- Python 3.11+
- Poetry (for development)

## Local Development

### Running with Docker

The easiest way to run the application is using Docker:

```bash
# Build and start the container
docker-compose up --build
```

The API will be available at http://localhost:8080

### Running locally (development)

```bash
# Install dependencies
cd apps/api
poetry install

# Install the model package
poetry add -e ../../packages/model

# Run the API
poetry run python main.py
```

## API Endpoints

- `POST /triage-image` - Upload an image for classification
- `GET /health` - Health check endpoint

## Example Usage

```bash
# Upload an image for classification
curl -X POST -F "file=@/path/to/your/image.jpg" http://localhost:8080/triage-image
```

Response:

```json
{
  "label": "acne",
  "confidence": 0.92,
  "processing_time_ms": 150
}
```

## Deployment (fly.io)

To deploy to fly.io:

1. Install the flyctl CLI tool
2. Log in to fly.io
3. Deploy the application:

```bash
flyctl deploy
```

## License

MIT
