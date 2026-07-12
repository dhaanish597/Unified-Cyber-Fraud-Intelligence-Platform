# api/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies (trimmed: excludes torch/torch_geometric, which are
# training-only and never imported at request-serving time — see
# requirements-render.txt for why. Keeps the image inside Render's free tier.)
COPY requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt

# Copy API source
COPY api/ api/
COPY ml/__init__.py ml/__init__.py
COPY ml/models/ ml/models/
COPY ml/features.py ml/features.py
COPY ml/predict.py ml/predict.py
COPY graph/ graph/

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
