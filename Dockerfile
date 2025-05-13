FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Create a non-root user
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Set working directory
WORKDIR /app

# Copy API pyproject.toml and poetry.lock files
COPY apps/api/pyproject.toml apps/api/poetry.lock* /app/

# Configure Poetry to install packages to the system
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Copy the model package
COPY packages/model /app/packages/model
RUN pip install -e /app/packages/model

# Copy the API application code
COPY apps/api /app/apps/api

# Set permissions for the appuser
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Set the working directory to the API code
WORKDIR /app/apps/api

# Command to run the application
CMD ["uvicorn", "main.app:app", "--host", "0.0.0.0", "--port", "8080"]
