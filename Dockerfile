FROM python:3.11-slim
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy the entire V70 Monorepo schema
COPY . .

# Install dependencies (Base system V67.1 + Flask + Gunicorn)
RUN pip install --no-cache-dir -r base_system_v67_1/requirements.txt
RUN pip install --no-cache-dir flask gunicorn requests pydantic pydantic-settings websockets

# Run the Flask app via Gunicorn binding to Render's exposed host
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--chdir", "base_system_v67_1/apps/enterprise_ui", "app:app"]
