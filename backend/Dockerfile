# QTD-HGNN backend image. Includes the shared `ml` package (features/graph/model
# reused at inference) and the trained artifacts. CPU-only torch.
FROM python:3.11-slim

WORKDIR /app

# system deps for scientific wheels (numpy/scipy/ripser runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# install python deps first (layer cache)
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# copy backend app, shared ml package, and trained artifacts
COPY backend/ ./backend/
COPY ml/ ./ml/

WORKDIR /app/backend
ENV PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/ml/artifacts \
    DATA_DIR=/app/ml/data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
