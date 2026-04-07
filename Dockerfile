FROM python:3.12-slim

# System deps for FastDownward, VAL binaries, and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ cmake make \
    libgmp-dev libboost-all-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer cache)
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY src/ /app/src/
COPY data/ /app/data/
COPY third-party/VAL/ /app/third-party/VAL/

# Ensure VAL binaries are executable
RUN chmod +x /app/third-party/VAL/build/linux64/Release/bin/*

# Create writable dirs
RUN mkdir -p /app/backend/tmp /app/results_web

# Expose API port (nginx proxies from outside)
EXPOSE 8001

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8001"]
