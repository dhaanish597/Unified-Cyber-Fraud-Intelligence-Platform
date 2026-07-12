# api/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API source
COPY api/ api/
COPY ml/models/ ml/models/
COPY ml/features.py ml/features.py
COPY ml/predict.py ml/predict.py
COPY graph/ graph/

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
