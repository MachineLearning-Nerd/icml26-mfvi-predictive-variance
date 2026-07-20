#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=2,<3", "pandas>=2,<3", "scipy>=1.12,<2"]
# ///
"""Independent, fail-closed audit for the three RG7maF4bGu jury claims.

This implementation intentionally does not import the author's posterior code.
It recomputes the Gaussian reverse-KL optimum, predictive variances, and
principal components with NumPy/SciPy.  The optional UCI mode uses every cached
input that the pinned official trace-inequality script uses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize


RNG_SEED = 20260720
NOISE_STD = 0.1
SPHERICAL_PRECISION = 1.0
DATASET_FILES = (
    "v1__boston__MEDV.pkl",
    "v1__concrete__ConcreteCompressiveStrength.pkl",
    "v1__energy__Y1.pkl",
    "v1__kin8nm___default.pkl",
    "v1__naval__kMc.pkl",
    "v1__power__PE.pkl",
    "v1__protein__RMSD.pkl",
    "v1__wine__class.pkl",
    "v1__yacht__residuary_resistance.pkl",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_default(value: object) -> object:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def posterior_and_mfvi(
    x: np.ndarray, prior_precision: np.ndarray | float = SPHERICAL_PRECISION
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return exact covariance, reverse-KL diagonal, and exact precision."""
    dimension = x.shape[1]
    if np.ndim(prior_precision) == 0:
        prior = float(prior_precision) * np.eye(dimension)
    else:
        prior = np.asarray(prior_precision, dtype=float)
    precision = x.T @ x / (NOISE_STD**2) + prior
    exact = np.linalg.solve(precision, np.eye(dimension))
    diagonal = 1.0 / np.diag(precision)
    return exact, diagonal, precision


def reverse_kl_from_log_diagonal(log_diagonal: np.ndarray, precision: np.ndarray) -> tuple[float, np.ndarray]:
    diagonal = np.exp(log_diagonal)
    precision_diagonal = np.diag(precision)
    value = 0.5 * (float(diagonal @ precision_diagonal) - float(log_diagonal.sum()))
    gradient = 0.5 * (diagonal * precision_diagonal - 1.0)
    return value, gradient


def audit_system(
    x: np.ndarray,
    *,
    prior_precision: np.ndarray | float = SPHERICAL_PRECISION,
    run_optimizer: bool,
) -> dict[str, float | bool | int]:
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 1:
        raise AssertionError(("invalid design shape", x.shape))
    if not np.isfinite(x).all():
        raise AssertionError("non-finite design")

    exact, diagonal, precision = posterior_and_mfvi(x, prior_precision)
    approximate = np.diag(diagonal)
    difference = approximate - exact
    covariance = x.T @ x / x.shape[0]
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    first_pc = eigenvectors[:, -1]
    empirical_gap = float(np.trace(covariance @ difference))
    first_pc_gap = float(first_pc @ difference @ first_pc)
    trace_gap = float(np.trace(difference))
    conserved_trace_error = abs(float(np.trace(precision @ approximate)) - x.shape[1])
    reverse_kl_gradient_error = float(
        np.max(np.abs(reverse_kl_from_log_diagonal(np.log(diagonal), precision)[1]))
    )
    marginal_diagonal = np.diag(exact)
    optimum_value, _ = reverse_kl_from_log_diagonal(np.log(diagonal), precision)
    marginal_value, _ = reverse_kl_from_log_diagonal(np.log(marginal_diagonal), precision)
    result: dict[str, float | bool | int] = {
        "n": int(x.shape[0]),
        "d": int(x.shape[1]),
        "empirical_mfvi_minus_exact_predictive_variance": empirical_gap,
        "first_pc_mfvi_minus_exact_predictive_variance": first_pc_gap,
        "mfvi_minus_exact_posterior_trace": trace_gap,
        "conserved_precision_trace_error": conserved_trace_error,
        "reverse_kl_stationarity_error": reverse_kl_gradient_error,
        "marginal_diagonal_reverse_kl_excess": float(marginal_value - optimum_value),
    }
    if run_optimizer:
        start = np.log(marginal_diagonal)

        def objective(log_diagonal: np.ndarray) -> tuple[float, np.ndarray]:
            return reverse_kl_from_log_diagonal(log_diagonal, precision)

        optimum = minimize(objective, start, jac=True, method="BFGS", options={"gtol": 1e-10})
        _, final_gradient = objective(np.asarray(optimum.x))
        # BFGS can emit its precision-loss status after it has already reached
        # an accurate stationary point in float64.  Judge the numerical result,
        # not that informational status string.
        if float(np.max(np.abs(final_gradient))) > 5e-8:
            raise AssertionError(("reverse-KL optimizer failed", optimum.message, final_gradient))
        result["optimizer_log_diagonal_error"] = float(
            np.max(np.abs(np.asarray(optimum.x) - np.log(diagonal)))
        )
    return result


def centered_standardized(frame: pd.DataFrame) -> np.ndarray:
    x = frame.to_numpy(dtype=float, copy=True)
    if not np.isfinite(x).all():
        raise AssertionError("cached UCI table is non-finite")
    # torch.std's default in the source is the Bessel-corrected sample standard
    # deviation, so this intentionally uses ddof=1 rather than NumPy's default.
    x = (x - x.mean(axis=0)) / (x.std(axis=0, ddof=1) + 1e-12)
    if not np.isfinite(x).all():
        raise AssertionError("standardization produced non-finite entries")
    return x


def verify_source_pins(paper_root: Path) -> dict[str, str]:
    source = json.loads((paper_root / "sources.json").read_text())
    upstream = paper_root / "upstream"
    commit = subprocess.check_output(
        ["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True
    ).strip()
    if commit != source["official_repository_commit"]:
        raise AssertionError(("official source commit mismatch", commit))
    verified: dict[str, str] = {"official_repository_commit": commit}
    data_root = upstream / "uci_data"
    for filename, expected in source["uci_data_sha256"].items():
        actual = sha256(data_root / filename)
        if actual != expected:
            raise AssertionError(("cached UCI input hash mismatch", filename, actual, expected))
        verified[filename] = actual
    return verified


def audit_uci(paper_root: Path) -> dict[str, Any]:
    verify_source_pins(paper_root)
    data_root = paper_root / "upstream" / "uci_data"
    rows: list[dict[str, Any]] = []
    for filename in DATASET_FILES:
        loaded = pd.read_pickle(data_root / filename)
        if not isinstance(loaded, tuple) or len(loaded) != 2:
            raise AssertionError(("expected cached (X,y) tuple", filename, type(loaded)))
        features, target = loaded
        if not isinstance(features, pd.DataFrame) or not isinstance(target, pd.DataFrame):
            raise AssertionError(("expected cached DataFrames", filename))
        if len(features) != len(target) or target.shape[1] != 1:
            raise AssertionError(("cached data shape mismatch", filename, features.shape, target.shape))
        row: dict[str, Any] = {"dataset_file": filename}
        row.update(audit_system(centered_standardized(features), run_optimizer=False))
        rows.append(row)

    tolerance = 5e-11
    if any(float(row["empirical_mfvi_minus_exact_predictive_variance"]) < -tolerance for row in rows):
        raise AssertionError(("empirical-distribution theorem failed", rows))
    if any(float(row["first_pc_mfvi_minus_exact_predictive_variance"]) < -tolerance for row in rows):
        raise AssertionError(("first-PC theorem failed", rows))
    if any(float(row["mfvi_minus_exact_posterior_trace"]) > tolerance for row in rows):
        raise AssertionError(("posterior-trace control failed", rows))
    if max(float(row["conserved_precision_trace_error"]) for row in rows) > 5e-10:
        raise AssertionError(("conserved precision trace failed", rows))
    return {
        "dataset_count": len(rows),
        "rows": rows,
        "minimum_empirical_gap": min(float(row["empirical_mfvi_minus_exact_predictive_variance"]) for row in rows),
        "minimum_first_pc_gap": min(float(row["first_pc_mfvi_minus_exact_predictive_variance"]) for row in rows),
        "maximum_trace_gap": max(float(row["mfvi_minus_exact_posterior_trace"]) for row in rows),
        "pass": True,
    }


def audit_synthetic() -> dict[str, Any]:
    rng = np.random.default_rng(RNG_SEED)
    systems: list[dict[str, float | bool | int]] = []
    for dimension in (2, 3, 5, 8, 13, 21, 34, 55, 64):
        eigenvalues = np.geomspace(0.05, 20.0, dimension)
        for replicate in range(16):
            rotation, _ = np.linalg.qr(rng.normal(size=(dimension, dimension)))
            x = rng.normal(size=(max(3 * dimension + 5, 80), dimension))
            x = x @ np.diag(np.sqrt(eigenvalues)) @ rotation.T
            x -= x.mean(axis=0, keepdims=True)
            systems.append(audit_system(x, run_optimizer=replicate == 0))

    tolerance = 2e-9
    if any(float(row["empirical_mfvi_minus_exact_predictive_variance"]) < -tolerance for row in systems):
        raise AssertionError("synthetic empirical-distribution theorem failed")
    if any(float(row["first_pc_mfvi_minus_exact_predictive_variance"]) < -tolerance for row in systems):
        raise AssertionError("synthetic first-PC theorem failed")
    if any(float(row["mfvi_minus_exact_posterior_trace"]) > tolerance for row in systems):
        raise AssertionError("synthetic posterior-trace control failed")
    if max(float(row["conserved_precision_trace_error"]) for row in systems) > 2e-9:
        raise AssertionError("synthetic conserved-trace identity failed")
    if max(float(row.get("optimizer_log_diagonal_error", 0.0)) for row in systems) > 2e-7:
        raise AssertionError("independent reverse-KL optimizer disagreed with analytic MFVI")

    # Axis-aligned posterior precisions are a destructive equality control:
    # MFVI must equal the exact posterior rather than report an artificial gain.
    axis = np.vstack((np.diag(np.linspace(0.2, 2.0, 11)), -np.diag(np.linspace(0.2, 2.0, 11))))
    axis_row = audit_system(axis, run_optimizer=True)
    if abs(float(axis_row["empirical_mfvi_minus_exact_predictive_variance"])) > 2e-12:
        raise AssertionError(("axis-aligned equality control failed", axis_row))

    # The first-PC statement depends on a spherical prior.  Search a deterministic
    # nonspherical counterexample and require that it genuinely reverses sign.
    nonspherical_counterexample: dict[str, float | bool | int] | None = None
    scope_rng = np.random.default_rng(RNG_SEED)
    for _ in range(128):
        dimension = 7
        rotation, _ = np.linalg.qr(scope_rng.normal(size=(dimension, dimension)))
        # Keep the likelihood weak enough that the deliberately non-spherical
        # prior can change which posterior direction is smallest.
        x = 0.005 * scope_rng.normal(size=(47, dimension)) @ rotation
        x -= x.mean(axis=0, keepdims=True)
        prior = np.diag(np.exp(scope_rng.uniform(-8.0, 8.0, size=dimension)))
        row = audit_system(x, prior_precision=prior, run_optimizer=False)
        if float(row["first_pc_mfvi_minus_exact_predictive_variance"]) < -1e-5:
            nonspherical_counterexample = row
            break
    if nonspherical_counterexample is None:
        raise AssertionError("failed to find deterministic nonspherical-prior scope control")

    return {
        "system_count": len(systems),
        "minimum_empirical_gap": min(float(row["empirical_mfvi_minus_exact_predictive_variance"]) for row in systems),
        "minimum_first_pc_gap": min(float(row["first_pc_mfvi_minus_exact_predictive_variance"]) for row in systems),
        "maximum_trace_gap": max(float(row["mfvi_minus_exact_posterior_trace"]) for row in systems),
        "axis_aligned_equality_control": axis_row,
        "nonspherical_prior_scope_control": nonspherical_counterexample,
        "pass": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--mode", choices=("synthetic", "uci", "full"), default="full")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    source_pins = verify_source_pins(arguments.paper_root)
    result: dict[str, Any] = {
        "paper": "RG7maF4bGu",
        "mode": arguments.mode,
        "methodology": {
            "implementation": "independent NumPy/SciPy reverse-KL and BLR audit",
            "rng_seed": RNG_SEED,
            "uses_author_posterior_code": False,
            "uses_all_released_cached_uci_inputs_when_uci_mode": arguments.mode in ("uci", "full"),
        },
        "source_pins": source_pins,
    }
    if arguments.mode in ("synthetic", "full"):
        result["synthetic"] = audit_synthetic()
    if arguments.mode in ("uci", "full"):
        result["uci"] = audit_uci(arguments.paper_root)
    result["pass"] = True

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, default=json_default, indent=2, sort_keys=True) + "\n"
    arguments.output.write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
