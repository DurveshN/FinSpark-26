"""Real topological features via persistent homology (ripser).

Computes Betti numbers b0/b1/b2 from a point cloud of feature vectors using a
Vietoris-Rips filtration. This is genuine TDA (not the old repo's variance+random)
and is the "shape of data" signal that gets appended to model features.
"""
from __future__ import annotations

import numpy as np
from ripser import ripser

# cap point-cloud size so real-time windows stay bounded (VR is superlinear).
# 200 keeps maxdim=1 Betti well under a second; H2 is dropped by default (near-always
# 0 here and the dominant cost). Callers pre-sort by relevance, so we keep the FIRST
# MAX_POINTS (deterministic) rather than a random sample that would break structure.
MAX_POINTS = 200
MIN_POINTS = 5


def _betti_from_diagram(dgm: np.ndarray, threshold: float) -> float:
    """Count features in a persistence diagram still 'alive' past a persistence threshold."""
    if dgm.size == 0:
        return 0.0
    births, deaths = dgm[:, 0], dgm[:, 1]
    finite = np.isfinite(deaths)
    persistence = np.where(finite, deaths - births, np.inf)
    return float(np.sum(persistence > threshold))


def betti_numbers(points: np.ndarray, maxdim: int = 1,
                  persistence_threshold: float = 0.15) -> dict[str, float]:
    """Return {'betti0','betti1','betti2'} for a point cloud (n_points x n_features).

    Betti_k counts k-dim holes that persist beyond `persistence_threshold`.
    b0 ~ connected clusters, b1 ~ loops (ring-like structure), b2 ~ voids.
    maxdim=1 by default (H2 is the dominant cost and ~always 0 on this data);
    betti2 is returned as 0.0 unless maxdim>=2 is requested explicitly.
    """
    pts = np.asarray(points, dtype=float)
    out = {"betti0": 0.0, "betti1": 0.0, "betti2": 0.0}
    if pts.ndim != 2 or pts.shape[0] < MIN_POINTS:
        out["betti0"] = float(max(pts.shape[0], 0) if pts.ndim == 2 else 0)
        return out

    if pts.shape[0] > MAX_POINTS:
        pts = pts[:MAX_POINTS]   # deterministic; callers pre-sort by relevance

    dgms = ripser(pts, maxdim=maxdim)["dgms"]
    for k in range(min(maxdim, 2) + 1):
        out[f"betti{k}"] = _betti_from_diagram(dgms[k], persistence_threshold) if k < len(dgms) else 0.0
    return out


def betti_curve(points: np.ndarray, dim: int = 1, n_bins: int = 10,
                max_radius: float | None = None) -> list[float]:
    """Vectorised Betti curve for dimension `dim`: count of alive features per radius bin.

    Used for the dashboard's live Betti area charts. Returns a length-n_bins vector.
    """
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 2 or pts.shape[0] < 3:
        return [0.0] * n_bins
    if pts.shape[0] > MAX_POINTS:
        pts = pts[:MAX_POINTS]   # deterministic; callers pre-sort by relevance

    dgms = ripser(pts, maxdim=max(dim, 1))["dgms"]
    if dim >= len(dgms) or dgms[dim].size == 0:
        return [0.0] * n_bins
    dgm = dgms[dim]
    finite_deaths = dgm[:, 1][np.isfinite(dgm[:, 1])]
    hi = max_radius if max_radius is not None else (float(finite_deaths.max()) if finite_deaths.size else 1.0)
    hi = hi or 1.0
    radii = np.linspace(0, hi, n_bins)
    curve = [float(np.sum((dgm[:, 0] <= r) & (dgm[:, 1] > r))) for r in radii]
    return curve
