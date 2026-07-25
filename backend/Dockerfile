# QTD-HGNN backend image. Includes the shared `ml` package (features/graph/model
# reused at inference) and the trained artifacts. CPU-only torch.
# Python 3.12 required: shap>=0.52 needs >=3.12 (torch+cpu and ripser have cp312 wheels).
FROM python:3.12-slim

WORKDIR /app

# system deps for scientific wheels (numpy/scipy/ripser runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# install python deps first (layer cache)
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# copy backend app + shared ml package (includes the committed trained model)
COPY backend/ ./backend/
COPY ml/ ./ml/

# Build-time: regenerate synthetic data (deterministic) + pre-score the whole
# dataset with the trained model. Bakes ml/data/*.csv + ml/artifacts/scored.csv +
# graph.pt into the image so runtime startup is instant (no scoring on the event
# loop) and the image is self-contained (works in CI where these are gitignored).
RUN python -m ml.prescore

WORKDIR /app/backend
ENV PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/ml/artifacts \
    DATA_DIR=/app/ml/data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
