"""Application settings loaded from environment (pydantic-settings).

Single place for env-driven config: database URL, CORS origin, model artifact path,
stream interval. No logic beyond reading env with sane local defaults.
"""
from __future__ import annotations

import os
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict

# repo root holds the shared `ml` package (features/graph/model reused at inference).
# Put it on sys.path so `import ml...` works regardless of CWD (local + Docker).
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

_DEFAULT_ARTIFACTS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "ml", "artifacts")
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./qtdhgnn.db"   # local default; Postgres in prod
    cors_origin: str = "*"                          # locked to Vercel origin in prod
    model_path: str = _DEFAULT_ARTIFACTS
    data_dir: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "ml", "data")
    )
    stream_interval_sec: float = 1.5               # dashboard telemetry cadence


settings = Settings()
