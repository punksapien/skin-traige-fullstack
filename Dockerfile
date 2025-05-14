# Dockerfile for skin-triage application

FROM python:3.11-slim

# 1. install tiny runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends libjpeg-dev && \
    rm -rf /var/lib/apt/lists/*

# 2. install python deps, no cache
COPY apps/api/requirements.txt /tmp/reqs.txt
RUN pip install --no-cache-dir -r /tmp/reqs.txt

# 3. copy code + model + static
WORKDIR /app

# Copy model package and model file first
COPY packages/model /app/packages/model
COPY packages/model/model.pth /app/packages/model/model.pth
RUN pip install -e /app/packages/model

# Copy API code and static files
COPY apps/api /app/
COPY apps/web/dist /app/static/

# 4. start
CMD ["uvicorn", "main.app:app", "--host", "0.0.0.0", "--port", "8080"]
