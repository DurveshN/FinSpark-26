"""Load and hold the trained QTD-HGNN artifacts in memory.

Loads model weights, the feature scaler (train mean/std + column order), and the
SHAP background sample once at startup. Provides the singleton other inference
modules use. No scoring logic here.
"""
from __future__ import annotations

import os
import numpy as np
import torch

from app.config import settings
from ml.models.gnn import QTDGraphSAGE


class ModelStore:
    def __init__(self) -> None:
        self.model: QTDGraphSAGE | None = None
        self.mean: np.ndarray | None = None
        self.std: np.ndarray | None = None
        self.cols: list[str] = []
        self.background: np.ndarray | None = None
        self.loaded = False

    def load(self) -> bool:
        """Load artifacts from settings.model_path. Returns True if successful."""
        path = settings.model_path
        model_file = os.path.join(path, "model.pt")
        scaler_file = os.path.join(path, "scaler.npz")
        if not (os.path.exists(model_file) and os.path.exists(scaler_file)):
            return False

        sc = np.load(scaler_file, allow_pickle=True)
        self.mean, self.std = sc["mean"], sc["std"]
        self.cols = [str(c) for c in sc["cols"]]

        model = QTDGraphSAGE(in_channels=len(self.cols))
        model.load_state_dict(torch.load(model_file, map_location="cpu"))
        model.eval()
        self.model = model

        bg_file = os.path.join(path, "shap_background.npy")
        self.background = np.load(bg_file) if os.path.exists(bg_file) else None
        self.loaded = True
        return True

    def standardize(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / self.std


store = ModelStore()
