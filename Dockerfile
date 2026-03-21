FROM python:3.11-slim
WORKDIR /workspace

# System Dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Transfer the entire V72 Monolithic application
COPY . .

# Ignite the V72 Unified Pipeline via Uvicorn native binding
CMD uvicorn backend.api.app:app --host 0.0.0.0 --port $PORT
