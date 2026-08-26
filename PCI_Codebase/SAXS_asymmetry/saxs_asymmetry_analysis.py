"""Native-grid diagnostics for one-dimensional SAXS left/right asymmetry.

The cleaned files contain aggregate line profiles, not individual shots.  The
functions below therefore report deterministic descriptors and sensitivity
checks rather than statistical confidence intervals.  Experimental runs are
never resampled onto one another: interpolation is used only to form mirrored
pairs inside the measured support of the run currently being analyzed.

The primary center and RMS metric are signal weighted.  This matters for
background-subtracted SAXS data because bins with almost zero signal can have
normalized asymmetry close to +/-1 despite carrying negligible scattered
intensity.  The legacy unweighted value is retained as a sensitivity metric.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pickle
from typing import Mapping

import numpy as np
from scipy.signal import savgol_filter


DEFAULT_SIDEBAND = (0.10, 0.38)
DEFAULT_Q_BANDS = {
    "low q (31-63 nm)": (0.10, 0.20),
    "mid q (21-31 nm)": (0.20, 0.30),
    "high q (17-21 nm)": (0.30, 0.38),
}


@dataclass(frozen=True)
class RunProfile:
    """One cleaned run in stored and reconstructed signed-q representations."""

    run: str
    q: np.ndarray
    intensity: np.ndarray
    q_positive: np.ndarray
    left: np.ndarray
    right: np.ndarray


@dataclass(frozen=True)
class MirroredProfile:
    """Matched samples around a trial symmetry center."""

    offsets: np.ndarray
    left: np.ndarray
    right: np.ndarray
    even: np.ndarray
    odd: np.ndarray
    normalized_odd: np.ndarray
    signal_weight: np.ndarray
    supported_signal: np.ndarray


def load_run_profile(run: str, path: str | Path) -> RunProfile:
    """Load ``(q_positive, left, right)`` and reconstruct native signed q.

    The left branch is reversed and assigned negative q.  Its duplicate zero
    bin is omitted.  Non-finite intensity bins are removed without replacing
    them by zeros, preserving the distinction between missing and measured
    background-subtracted data.
    """
    path = Path(path)
    with path.open("rb") as stream:
        payload = pickle.load(stream)
    if not isinstance(payload, (tuple, list)) or len(payload) < 3:
        raise ValueError(f"{path.name} must contain (q_positive, left, right).")

    q_positive, left, right = (
        np.asarray(value, dtype=np.float64).squeeze() for value in payload[:3]
    )
    arrays = (q_positive, left, right)
    if any(array.ndim != 1 for array in arrays):
        raise ValueError(f"{path.name} components must be one-dimensional.")
    if len({array.size for array in arrays}) != 1 or q_positive.size < 3:
        raise ValueError(f"{path.name} components have invalid lengths.")
    if not np.all(np.isfinite(q_positive)):
        raise ValueError(f"{path.name} contains a non-finite q coordinate.")
    if q_positive[0] != 0 or np.any(np.diff(q_positive) <= 0):
        raise ValueError(f"{path.name} q_positive must start at zero and increase.")

    q = np.concatenate((-q_positive[:0:-1], q_positive))
    intensity = np.concatenate((left[:0:-1], right))
    finite = np.isfinite(intensity)
    q = q[finite]
    intensity = intensity[finite]
    if q.size < 3 or np.any(np.diff(q) <= 0):
        raise ValueError(f"{path.name} does not yield a valid signed q profile.")
    return RunProfile(run, q, intensity, q_positive, left, right)


def load_profiles(run_files: Mapping[str, str | Path]) -> dict[str, RunProfile]:
    """Load a mapping without introducing a shared experimental q grid."""
    return {run: load_run_profile(run, path) for run, path in run_files.items()}


def mirrored_components(
    q,
    intensity,
    center: float,
    sideband=DEFAULT_SIDEBAND,
    samples: int = 321,
    signal_floor_fraction: float = 0.01,
) -> MirroredProfile:
    """Evaluate even and odd components strictly inside one run's q support.

    ``signal_weight`` is the sum of the non-negative parts of the two measured
    branches.  Negative values can occur after background subtraction; they
    are retained in even/odd amplitudes but cannot represent negative photon
    counts and therefore receive zero statistical/flux weight.
    """
    q = np.asarray(q, dtype=np.float64)
    intensity = np.asarray(intensity, dtype=np.float64)
    if q.ndim != 1 or intensity.shape != q.shape or q.size < 3:
        raise ValueError("q and intensity must be equal-length one-dimensional arrays.")
    if not np.all(np.isfinite(q)) or not np.all(np.isfinite(intensity)):
        raise ValueError("q and intensity must contain finite samples.")
    if np.any(np.diff(q) <= 0):
        raise ValueError("q must be strictly increasing.")
    q_min, q_max = map(float, sideband)
    if not 0 <= q_min < q_max or samples < 3:
        raise ValueError("sideband and sample count are invalid.")
    if not 0 <= signal_floor_fraction < 1:
        raise ValueError("signal_floor_fraction must lie in [0, 1).")

    supported_max = min(center - q[0], q[-1] - center, q_max)
    if supported_max <= q_min:
        raise ValueError("Trial center leaves no valid mirrored sideband.")
    supported_max = np.nextafter(supported_max, 0.0)
    offsets = np.linspace(q_min, supported_max, samples)
    q_left = center - offsets
    q_right = center + offsets
    if q_left.min() < q[0] or q_right.max() > q[-1]:
        raise RuntimeError("Mirrored coordinates exceeded measured q support.")

    left = np.interp(q_left, q, intensity)
    right = np.interp(q_right, q, intensity)
    even = 0.5 * (right + left)
    odd = 0.5 * (right - left)
    denominator_floor = max(np.finfo(float).eps, 1e-12 * np.max(np.abs(intensity)))
    normalized_odd = (right - left) / np.maximum(
        np.abs(right) + np.abs(left), denominator_floor
    )
    signal_weight = np.clip(left, 0, None) + np.clip(right, 0, None)
    peak_signal = float(np.max(signal_weight))
    if peak_signal <= 0:
        raise ValueError("Mirrored sideband contains no positive measured signal.")
    supported_signal = signal_weight >= signal_floor_fraction * peak_signal
    return MirroredProfile(
        offsets,
        left,
        right,
        even,
        odd,
        normalized_odd,
        signal_weight,
        supported_signal,
    )


def asymmetry_score(
    center,
    q,
    intensity,
    sideband=DEFAULT_SIDEBAND,
    *,
    signal_weighted=True,
) -> float:
    """Return mean squared normalized odd signal for center optimization."""
    component = mirrored_components(q, intensity, center, sideband=sideband)
    if not signal_weighted:
        return float(np.mean(component.normalized_odd**2))
    numerator = np.trapezoid(
        component.signal_weight * component.normalized_odd**2,
        component.offsets,
    )
    denominator = np.trapezoid(component.signal_weight, component.offsets)
    return float(numerator / denominator) if denominator > 0 else float("inf")


def estimate_symmetry_center(
    q,
    intensity,
    sideband=DEFAULT_SIDEBAND,
    maximum_shift=0.03,
    refinements=4,
    signal_weighted=True,
):
    """Find a descriptive center using a deterministic coarse-to-fine search.

    The objective sideband is fixed for every candidate.  Consequently, a
    candidate cannot improve merely by losing high-q samples at the boundary.
    """
    if maximum_shift <= 0 or refinements < 1:
        raise ValueError("maximum_shift and refinements must be positive.")
    q = np.asarray(q, dtype=float)
    requested_min, requested_max = sideband
    candidate_safe_max = min(
        requested_max,
        -maximum_shift - q[0],
        q[-1] - maximum_shift,
    )
    if candidate_safe_max <= requested_min:
        raise ValueError("Search interval has no common mirrored q support.")
    fixed_sideband = (requested_min, candidate_safe_max)

    absolute_lower, absolute_upper = -maximum_shift, maximum_shift
    lower, upper = absolute_lower, absolute_upper
    best_center = 0.0
    best_score = float("inf")
    for _ in range(refinements):
        candidates = np.linspace(lower, upper, 401)
        scores = np.array(
            [
                asymmetry_score(
                    candidate,
                    q,
                    intensity,
                    fixed_sideband,
                    signal_weighted=signal_weighted,
                )
                for candidate in candidates
            ]
        )
        best_index = int(np.argmin(scores))
        best_center = float(candidates[best_index])
        best_score = float(scores[best_index])
        step = float(candidates[1] - candidates[0])
        lower = max(absolute_lower, best_center - step)
        upper = min(absolute_upper, best_center + step)
    return best_center, best_score, fixed_sideband


def component_metrics(component: MirroredProfile) -> dict[str, float]:
    """Compute flux-aware and legacy descriptors for one mirrored sideband."""
    offsets = component.offsets
    weight = component.signal_weight
    weight_integral = np.trapezoid(weight, offsets)
    if weight_integral <= 0:
        raise ValueError("Cannot normalize a sideband with zero positive signal.")
    supported = component.supported_signal
    positive_left = np.clip(component.left, 0, None)
    positive_right = np.clip(component.right, 0, None)
    weighted_rms = np.sqrt(
        np.trapezoid(weight * component.normalized_odd**2, offsets) / weight_integral
    )
    signed_flux = np.trapezoid(positive_right - positive_left, offsets) / weight_integral
    absolute_flux = np.trapezoid(
        np.abs(positive_right - positive_left), offsets
    ) / weight_integral
    cosine_denominator = np.linalg.norm(positive_left) * np.linalg.norm(positive_right)
    mirror_cosine = (
        float(np.dot(positive_left, positive_right) / cosine_denominator)
        if cosine_denominator > 0
        else np.nan
    )
    even_area = np.trapezoid(np.abs(component.even), offsets)
    odd_area = np.trapezoid(np.abs(component.odd), offsets)
    return {
        "weighted_rms": float(weighted_rms),
        "supported_rms": float(np.sqrt(np.mean(component.normalized_odd[supported] ** 2))),
        "legacy_unweighted_rms": float(np.sqrt(np.mean(component.normalized_odd**2))),
        "peak_supported_asymmetry": float(np.max(np.abs(component.normalized_odd[supported]))),
        "signed_flux_asymmetry": float(signed_flux),
        "absolute_flux_asymmetry": float(absolute_flux),
        "mirror_cosine": mirror_cosine,
        "odd_even_area_ratio": float(odd_area / even_area) if even_area > 0 else np.nan,
        "supported_fraction": float(np.mean(supported)),
    }


def shift_gain_decomposition(
    q,
    intensity,
    sideband=DEFAULT_SIDEBAND,
    signal_floor_fraction=0.01,
):
    """Decompose nominal-center odd signal into shift-like and gain-like terms.

    For a slightly displaced symmetric profile ``S(q-q_shift)``, the mirrored
    odd component is approximately ``-q_shift*dS/dq``.  A multiplicative
    left/right imbalance contributes a term proportional to the even profile.
    Weighted least squares fits both basis functions about nominal q=0.  The
    residual is descriptive: detector response, morphology, background, and
    model inadequacy can all contribute, so it is not uniquely structural.
    """
    component = mirrored_components(
        q,
        intensity,
        0.0,
        sideband=sideband,
        signal_floor_fraction=signal_floor_fraction,
    )
    count = component.offsets.size
    window = min(31, count if count % 2 else count - 1)
    window = max(window, 5)
    spacing = float(component.offsets[1] - component.offsets[0])
    smooth_even = savgol_filter(component.even, window, 3)
    derivative = savgol_filter(component.even, window, 3, deriv=1, delta=spacing)
    use = component.supported_signal
    weights = component.signal_weight[use]
    weights = weights / np.max(weights)
    design = np.column_stack((-derivative[use], smooth_even[use]))
    weighted_design = design * np.sqrt(weights)[:, None]
    weighted_odd = component.odd[use] * np.sqrt(weights)
    coefficients, *_ = np.linalg.lstsq(weighted_design, weighted_odd, rcond=None)
    prediction = design @ coefficients
    residual = component.odd[use] - prediction
    odd_energy = np.sum(weights * component.odd[use] ** 2)
    residual_energy = np.sum(weights * residual**2)
    explained_fraction = 1 - residual_energy / odd_energy if odd_energy > 0 else np.nan
    return {
        "apparent_shift": float(coefficients[0]),
        "gain_imbalance": float(coefficients[1]),
        "explained_odd_fraction": float(explained_fraction),
        "offsets": component.offsets,
        "observed_odd": component.odd,
        "smooth_even": smooth_even,
        "modeled_odd_supported": prediction,
        "supported_mask": use,
    }


def local_log_slope(profile: RunProfile, q_band=(0.20, 0.38)) -> dict[str, dict[str, float]]:
    """Fit descriptive ``d ln(I)/d ln(q)`` slopes on each stored branch.

    This is not labeled a Porod exponent because a Porod regime and background
    model have not been established.  Poor R-squared values explicitly warn
    against interpreting the fitted slope as interface physics.
    """
    results = {}
    for label, values in (("left", profile.left), ("right", profile.right)):
        use = (
            (profile.q_positive >= q_band[0])
            & (profile.q_positive <= q_band[1])
            & np.isfinite(values)
            & (values > 0)
        )
        if np.count_nonzero(use) < 3:
            results[label] = {"slope": np.nan, "r_squared": np.nan, "samples": int(use.sum())}
            continue
        x = np.log(profile.q_positive[use])
        y = np.log(values[use])
        slope, intercept = np.polyfit(x, y, 1)
        predicted = slope * x + intercept
        total = np.sum((y - np.mean(y)) ** 2)
        residual = np.sum((y - predicted) ** 2)
        results[label] = {
            "slope": float(slope),
            "r_squared": float(1 - residual / total) if total > 0 else np.nan,
            "samples": int(use.sum()),
        }
    return results


def analyze_profile(
    profile: RunProfile,
    sideband=DEFAULT_SIDEBAND,
    q_bands=DEFAULT_Q_BANDS,
) -> dict:
    """Return complementary center, flux, scale, and shape diagnostics."""
    center, center_score, fixed_sideband = estimate_symmetry_center(
        profile.q, profile.intensity, sideband=sideband, signal_weighted=True
    )
    legacy_center, legacy_score, _ = estimate_symmetry_center(
        profile.q, profile.intensity, sideband=sideband, signal_weighted=False
    )
    component = mirrored_components(
        profile.q, profile.intensity, center, sideband=fixed_sideband
    )
    metrics = component_metrics(component)
    band_metrics = {}
    for label, band in q_bands.items():
        band_component = mirrored_components(
            profile.q, profile.intensity, center, sideband=band, samples=161
        )
        band_metrics[label] = component_metrics(band_component)
    return {
        "center": center,
        "center_score": center_score,
        "legacy_center": legacy_center,
        "legacy_center_score": legacy_score,
        "center_method_difference": center - legacy_center,
        "objective_sideband": fixed_sideband,
        "component": component,
        **metrics,
        "band_metrics": band_metrics,
        "shift_gain": shift_gain_decomposition(profile.q, profile.intensity, sideband=fixed_sideband),
        "local_log_slope": local_log_slope(profile),
    }


def analyze_profiles(profiles: Mapping[str, RunProfile]) -> dict[str, dict]:
    """Analyze every run independently on its native measured q coordinates."""
    return {run: analyze_profile(profile) for run, profile in profiles.items()}
