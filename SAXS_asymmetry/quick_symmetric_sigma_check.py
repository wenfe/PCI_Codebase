"""Quickly compare symmetric wire-edge sigmas for divergent Mark1300 SAXS.

The script uses beam/wire separability to calculate the Mark1300 left fraction
with inexpensive one-dimensional FFTs and overlays Erik's measured motor scan.

Run from the repository root with::

    python SAXS_asymmetry/quick_symmetric_sigma_check.py

By default it compares sigma = 0, 3, 4, 6, 8, and 14 nm for the
7.11 um beam case with a +0.005 nm^-1 Mark1300 q-mask shift. The scan uses
0.48 um wire-offset spacing from -10.0 through +10.16 um. Results are written to
``SAXS_asymmetry/outputs/quick_symmetric_sigma``.
Fraction plots and wire-thickness plots are saved as separate figures with
consistent rainbow sigma colors. Separate 8-by-6-inch wire-thickness figures
zoom onto the left and right edges and use the filename suffixes
``_wire_left_edge`` and ``_wire_right_edge``.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter1d, shift as nd_shift


SAXS_DIR = Path(__file__).resolve().parent
if str(SAXS_DIR) not in sys.path:
    sys.path.insert(0, str(SAXS_DIR))

import PCI  # noqa: E402  (PCI.py lives beside this script)


GRID_SIZE = 4096
PIXEL_SIZE_NM = 8.0
WIRE_RADIUS_NM = 5.0 * PCI.um
WIRE_VOXEL_SIZE_NM = 8.0
WIRE_VOXEL_NUMBER = 2000
PHOTON_ENERGY_KEV = 8.2
WAVELENGTH_NM = PCI.HC_KEV_NM / PHOTON_ENERGY_KEV
Z_TARGET_NM = 0.25 * PCI.m
Z_SAXS_DETECTOR_NM = 1.31 * PCI.m
Q_STEP_NM_INV = 2.0 * np.pi / (GRID_SIZE * PIXEL_SIZE_NM)
MARK1300_Q_MIN_NM_INV = 0.10
Q_MASK_SHIFT_NM_INV = 0.005
OFFSET_STEP_UM = 0.48
OFFSET_MIN_UM = -10.0
OFFSET_MAX_UM = 10.16

DEFAULT_OUTPUT_DIR = SAXS_DIR / "outputs" / "quick_symmetric_sigma"
ERIK_DIR = SAXS_DIR / "inputs" / "experimental" / "Erik"
MARK1300_BEAM_CASES = {
    "7p11um": 7.11,
}


def load_erik_motor_reference() -> dict[str, np.ndarray]:
    """Load the motor-scan offsets and measured left fraction used in notebook 02."""
    paths = {
        "motor_offsets_um": ERIK_DIR / "motor_positions_um.npy",
        "motor_left_fraction": ERIK_DIR / "left_div_left_right_exp.npy",
    }
    missing = [path for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing Erik motor reference file(s): "
            + ", ".join(str(path) for path in missing)
        )
    erik = {name: np.asarray(np.load(path), dtype=float) for name, path in paths.items()}
    if erik["motor_offsets_um"].shape != erik["motor_left_fraction"].shape:
        raise ValueError("Erik motor offsets and left fractions must have matching shapes.")
    if not all(np.all(np.isfinite(values)) for values in erik.values()):
        raise ValueError("Erik motor reference contains non-finite values.")
    return erik


def voxelized_chord_profile() -> np.ndarray:
    """Return the same voxelized 10 um wire chord used by notebook 01."""
    transverse_px = np.arange(WIRE_VOXEL_NUMBER) - WIRE_VOXEL_NUMBER // 2
    radius_px = WIRE_RADIUS_NM / WIRE_VOXEL_SIZE_NM
    inside = np.clip(radius_px**2 - transverse_px**2, 0.0, None)
    return np.where(
        np.abs(transverse_px) <= radius_px,
        2.0 * np.sqrt(inside) * WIRE_VOXEL_SIZE_NM,
        0.0,
    )


def symmetric_blur(profile: np.ndarray, sigma_nm: float) -> np.ndarray:
    """Apply the same constant-boundary Gaussian blur used by notebook 01."""
    if sigma_nm < 0:
        raise ValueError("Sigma values must be non-negative.")
    if sigma_nm == 0:
        return profile.copy()
    return gaussian_filter1d(
        profile,
        sigma=sigma_nm / WIRE_VOXEL_SIZE_NM,
        mode="constant",
        cval=0.0,
        truncate=3.0,
    )


def asymmetric_blur(
    profile: np.ndarray, sigma_left_nm: float, sigma_right_nm: float
) -> np.ndarray:
    """Join independently blurred halves, matching notebook 01."""
    left_profile = symmetric_blur(profile, sigma_left_nm)
    right_profile = symmetric_blur(profile, sigma_right_nm)
    centered_axis = np.arange(profile.size) - profile.size // 2
    return np.where(centered_axis <= 0, left_profile, right_profile)


def source_waist_for_target_fwhm(fwhm_um: float) -> float:
    """Return the divergent Gaussian source waist used by notebook 01."""
    target_radius_nm = fwhm_um * PCI.um / np.sqrt(2.0 * np.log(2.0))
    diffraction_term = WAVELENGTH_NM * Z_TARGET_NM / np.pi
    discriminant = max(target_radius_nm**4 - 4.0 * diffraction_term**2, 0.0)
    return float(
        np.sqrt((target_radius_nm**2 - np.sqrt(discriminant)) / 2.0)
    )


def gaussian_target_line_field(fwhm_um: float) -> np.ndarray:
    """Generate the exact central target-plane Gaussian field in one dimension."""
    waist_nm = source_waist_for_target_fwhm(fwhm_um)
    rayleigh_nm = np.pi * waist_nm**2 / WAVELENGTH_NM
    radius_nm = (Z_TARGET_NM**2 + rayleigh_nm**2) / Z_TARGET_NM
    spot_radius_nm = waist_nm * np.sqrt(1.0 + Z_TARGET_NM**2 / rayleigh_nm**2)
    q_parameter_nm = 1.0 / (
        1.0 / radius_nm
        - 1j * WAVELENGTH_NM / (np.pi * spot_radius_nm**2)
    )
    axis_nm = (np.arange(GRID_SIZE) - GRID_SIZE // 2) * PIXEL_SIZE_NM
    return (
        1.0
        / q_parameter_nm
        * np.exp(
            -1j
            * 2.0
            * np.pi
            / WAVELENGTH_NM
            * axis_nm**2
            / (2.0 * q_parameter_nm)
        )
    )


def mark1300_left_fraction_scan(
    fwhm_um: float,
    offsets_um: np.ndarray,
    sigma_left_nm: float,
    sigma_right_nm: float,
    q_mask_shift_nm_inv: float = Q_MASK_SHIFT_NM_INV,
) -> np.ndarray:
    """Calculate the divergent Mark1300 fraction with an exact 1-D reduction.

    The Gaussian beam and straight wire are separable in x and y.  Consequently
    the y Fourier factor cancels from L/(L+R), making this 1-D FFT equivalent to
    the central-row fraction of notebook 01's 2-D Lorentz propagation.
    """
    copper = PCI.Cu()
    field_at_target = gaussian_target_line_field(fwhm_um)
    axis_nm = (np.arange(GRID_SIZE) - GRID_SIZE // 2) * PIXEL_SIZE_NM
    target_axis_nm = (
        np.arange(WIRE_VOXEL_NUMBER) - WIRE_VOXEL_NUMBER // 2
    ) * WIRE_VOXEL_SIZE_NM
    centered_chord_nm = asymmetric_blur(
        voxelized_chord_profile(), sigma_left_nm, sigma_right_nm
    )
    amplitude_mu_per_nm = (
        copper.get_n_refraction_beta(PHOTON_ENERGY_KEV)
        * PHOTON_ENERGY_KEV
        * 10.0
    )
    phase_per_nm = (
        2.0
        * np.pi
        / (1.239842 / PHOTON_ENERGY_KEV)
        * copper.get_n_refraction_delta(PHOTON_ENERGY_KEV)
    )
    wave_number_nm_inv = 2.0 * np.pi / WAVELENGTH_NM
    quadratic_phase = np.exp(
        1j * wave_number_nm_inv * axis_nm**2 / (2.0 * Z_SAXS_DETECTOR_NM)
    )
    q_axis_nm_inv = (np.arange(GRID_SIZE) - GRID_SIZE // 2) * Q_STEP_NM_INV
    left_edge_nm_inv = q_mask_shift_nm_inv - MARK1300_Q_MIN_NM_INV
    right_edge_nm_inv = q_mask_shift_nm_inv + MARK1300_Q_MIN_NM_INV
    left_weights = np.clip(
        (left_edge_nm_inv - q_axis_nm_inv) / Q_STEP_NM_INV + 0.5,
        0.0,
        1.0,
    )
    right_weights = np.clip(
        (q_axis_nm_inv - right_edge_nm_inv) / Q_STEP_NM_INV + 0.5,
        0.0,
        1.0,
    )

    fractions = np.empty(offsets_um.size, dtype=float)
    for index, offset_um in enumerate(offsets_um):
        shifted_chord_nm = nd_shift(
            centered_chord_nm,
            offset_um * PCI.um / WIRE_VOXEL_SIZE_NM,
            order=1,
            mode="constant",
            cval=0.0,
            prefilter=False,
        )
        thickness_nm = np.interp(
            axis_nm,
            target_axis_nm,
            shifted_chord_nm,
            # RectBivariateSpline in the full 2-D SAXS path holds the target's
            # boundary value outside its tabulated grid.  Preserve that detail
            # here, especially for wire offsets beyond about +/-3 um.
            left=float(shifted_chord_nm[0]),
            right=float(shifted_chord_nm[-1]),
        )
        contact_field = field_at_target * np.exp(
            -0.5 * amplitude_mu_per_nm * thickness_nm
            - 1j * phase_per_nm * thickness_nm
        )
        detector_lineout = np.abs(
            np.fft.fftshift(np.fft.fft(contact_field * quadratic_phase))
        ) ** 2
        left = float(np.sum(detector_lineout * left_weights))
        right = float(np.sum(detector_lineout * right_weights))
        fractions[index] = left / (left + right)

    return fractions


def validate_mark1300_reduction() -> None:
    """Compare the shifted-mask 1-D reduction with saved full 2-D data."""
    table_dir = (
        SAXS_DIR
        / "outputs"
        / "sigmaL_4nm_sigmaR_8nm"
        / "clean_pci"
    )
    validation_cases = {
        6.0: table_dir / "mark1300_6p0um_shifted_q_mask_left_fraction.dat",
        7.11: table_dir / "mark1300_7p11um_shifted_q_mask_left_fraction.dat",
    }
    for beam_fwhm_um, table_path in validation_cases.items():
        if not table_path.exists():
            continue
        saved = np.loadtxt(table_path)
        saved_offsets_um = saved[:, 0]
        saved_fraction = saved[:, 1]
        reduced_fraction = mark1300_left_fraction_scan(
            beam_fwhm_um,
            saved_offsets_um,
            sigma_left_nm=4.0,
            sigma_right_nm=8.0,
            q_mask_shift_nm_inv=Q_MASK_SHIFT_NM_INV,
        )
        max_error = float(np.max(np.abs(reduced_fraction - saved_fraction)))
        if max_error > 3e-7:
            raise RuntimeError(
                "The quick Mark1300 reduction does not match the saved full "
                f"2-D result for {beam_fwhm_um:g} um: max error {max_error:.3g}."
            )
        print(
            "Validated quick Mark1300 reduction against full 2-D result "
            f"({beam_fwhm_um:g} um; max error {max_error:.3g})."
        )


def save_scan_table(
    path: Path,
    offsets_um: np.ndarray,
    sigmas_nm: tuple[float, ...],
    fractions: dict[float, np.ndarray],
    q_mask_shift_nm_inv: float,
) -> None:
    header = ["offset_um"] + [f"left_fraction_sigma_{sigma:g}nm" for sigma in sigmas_nm]
    columns = [offsets_um] + [fractions[sigma] for sigma in sigmas_nm]
    np.savetxt(
        path,
        np.column_stack(columns),
        header=(
            f"q_mask_shift_nm_inv={q_mask_shift_nm_inv:g}\n"
            + " ".join(header)
        ),
        fmt="%.10g",
    )


def save_selected_offset_summary(
    path: Path,
    results: dict[str, dict[str, object]],
    sigmas_nm: tuple[float, ...],
    q_mask_shift_nm_inv: float,
    selected_offsets_um: tuple[float, ...] = (-2.0, 0.0, 2.0),
) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "beam_fwhm_um",
                "sigma_nm",
                "q_mask_shift_nm_inv",
                "requested_offset_um",
                "sampled_offset_um",
                "left_fraction",
            ]
        )
        for result in results.values():
            beam_fwhm_um = float(result["beam_fwhm_um"])
            offsets_um = np.asarray(result["offsets_um"])
            fraction_by_sigma = result["fraction_by_sigma"]
            for sigma_nm in sigmas_nm:
                fractions = fraction_by_sigma[sigma_nm]
                for selected_offset_um in selected_offsets_um:
                    index = int(np.argmin(np.abs(offsets_um - selected_offset_um)))
                    writer.writerow(
                        [
                            f"{beam_fwhm_um:g}",
                            f"{sigma_nm:g}",
                            f"{q_mask_shift_nm_inv:g}",
                            f"{selected_offset_um:g}",
                            f"{offsets_um[index]:g}",
                            f"{fractions[index]:.10g}",
                        ]
                    )


def save_sigma_effect_summary(
    path: Path,
    results: dict[str, dict[str, object]],
    sigmas_nm: tuple[float, ...],
    q_mask_shift_nm_inv: float,
) -> None:
    """Report each curve's largest absolute difference from the 8 nm case."""
    reference_sigma_nm = 8.0 if 8.0 in sigmas_nm else sigmas_nm[0]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "beam_fwhm_um",
                "sigma_nm",
                "q_mask_shift_nm_inv",
                "reference_sigma_nm",
                "max_abs_left_fraction_change",
                "offset_at_max_um",
            ]
        )
        for result in results.values():
            beam_fwhm_um = float(result["beam_fwhm_um"])
            offsets_um = np.asarray(result["offsets_um"])
            fraction_by_sigma = result["fraction_by_sigma"]
            reference = fraction_by_sigma[reference_sigma_nm]
            for sigma_nm in sigmas_nm:
                difference = fraction_by_sigma[sigma_nm] - reference
                index = int(np.argmax(np.abs(difference)))
                writer.writerow(
                    [
                        f"{beam_fwhm_um:g}",
                        f"{sigma_nm:g}",
                        f"{q_mask_shift_nm_inv:g}",
                        f"{reference_sigma_nm:g}",
                        f"{abs(difference[index]):.10g}",
                        f"{offsets_um[index]:.10g}",
                    ]
                )


def save_comparison_plot(
    path: Path,
    results: dict[str, dict[str, object]],
    sigmas_nm: tuple[float, ...],
    *,
    title: str,
    fraction_label: str,
    motor_offsets_um: np.ndarray | None = None,
    motor_left_fraction: np.ndarray | None = None,
) -> list[Path]:
    import matplotlib.pyplot as plt
    # Keep nearby sigma cases distinct, with the same colors in all figures.
    colors = plt.get_cmap("rainbow")(np.linspace(0.0, 1.0, len(sigmas_nm)))
    sigma_colors = dict(zip(sigmas_nm, colors))
    sigma_labels = {
        sigma_nm: rf"$\sigma_L=\sigma_R={sigma_nm:g}$ nm"
        for sigma_nm in sigmas_nm
    }
    wire_axis_um = (
        (np.arange(WIRE_VOXEL_NUMBER) - WIRE_VOXEL_NUMBER // 2)
        * WIRE_VOXEL_SIZE_NM / PCI.um
    )
    unblurred_chord_nm = voxelized_chord_profile()
    thickness_profiles_um = {
        sigma_nm: symmetric_blur(unblurred_chord_nm, sigma_nm) / PCI.um
        for sigma_nm in sigmas_nm
    }
    output_paths: list[Path] = []
    for column, result in enumerate(results.values()):
        figure, fraction_axis = plt.subplots(
            figsize=(10.8, 4.8), layout="constrained"
        )
        offsets_um = np.asarray(result["offsets_um"])
        fraction_by_sigma = result["fraction_by_sigma"]
        for sigma_nm in sigmas_nm:
            fraction_axis.plot(
                offsets_um,
                fraction_by_sigma[sigma_nm],
                color=sigma_colors[sigma_nm],
                label=sigma_labels[sigma_nm],
            )
        if motor_offsets_um is not None and motor_left_fraction is not None:
            fraction_axis.plot(
                motor_offsets_um,
                motor_left_fraction,
                "kx",
                markersize=5,
                markeredgewidth=1.0,
                linestyle="none",
                label="Experiment (motor scan)",
                zorder=5,
            )
        fraction_axis.axhline(0.5, color="0.5", linewidth=0.8, linestyle="--")
        # fraction_axis.set_title(
        #     f"Beam FWHM {float(result['beam_fwhm_um']):g} µm"
        # )
        fraction_axis.set(
            xlabel="Wire offset (µm)",
            ylabel=fraction_label,
        )
        fraction_axis.grid(alpha=0.25)
        fraction_axis.legend(frameon=False, fontsize=9)

        figure.suptitle(title)
        output_path = path if len(results) == 1 else path.with_name(
            f"{path.stem}_{column}{path.suffix}"
        )
        figure.savefig(output_path, dpi=180, bbox_inches="tight")
        plt.close(figure)
        output_paths.append(output_path)

    # Wire-edge profiles depend on sigma, not on the beam case.
    for edge_name, edge_slug, edge_limits_um in (
        ("Left edge", "left", (-5.04, -4.99)),
        ("Right edge", "right", (4.99, 5.04)),
    ):
        thickness_figure = plt.figure(figsize=(8, 6), layout="constrained")
        thickness_axis = thickness_figure.gca()
        for sigma_nm in sigmas_nm:
            thickness_axis.plot(
                wire_axis_um,
                thickness_profiles_um[sigma_nm],
                color=sigma_colors[sigma_nm],
                linewidth=2,
                label=sigma_labels[sigma_nm],
            )
        thickness_axis.set(
            xlabel="Distance across wire [µm]",
            title=f"{edge_name} wire-edge blur",
            xlim=edge_limits_um,
            ylim=(0.0, 0.2),
        )
        thickness_axis.grid(alpha=0.25)
        thickness_axis.set_ylabel("Wire thickness [µm]")
        thickness_axis.legend(
            loc="upper left" if edge_slug == "left" else "upper right",
            fontsize=8,
        )
        thickness_figure.suptitle(title)
        thickness_path = path.with_name(
            f"{path.stem}_wire_{edge_slug}_edge{path.suffix}"
        )
        thickness_figure.savefig(thickness_path, dpi=180, bbox_inches="tight")
        plt.close(thickness_figure)
        output_paths.append(thickness_path)
    return output_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sigmas",
        nargs="+",
        type=float,
        default=[0.0, 3.0, 4.0, 6.0, 8.0, 14.0],
        help="Symmetric sigma values in nm (default: 0 3 4 6 8 14).",
    )
    parser.add_argument(
        "--q-mask-shift-nm-inv",
        type=float,
        default=Q_MASK_SHIFT_NM_INV,
        help="Mark1300 q-mask-centre shift in nm^-1 (default: 0.005).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Destination for tables and separate fraction and wire-edge figures.",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Write tables without creating the PNG figures.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sigmas_nm = tuple(float(value) for value in args.sigmas)
    q_mask_shift_nm_inv = float(args.q_mask_shift_nm_inv)
    if not sigmas_nm or any(value < 0 for value in sigmas_nm):
        raise ValueError("Provide one or more non-negative sigma values.")
    if len(set(sigmas_nm)) != len(sigmas_nm):
        raise ValueError("Sigma values must be unique.")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    offsets_um = np.arange(
        OFFSET_MIN_UM,
        OFFSET_MAX_UM + 0.5 * OFFSET_STEP_UM,
        OFFSET_STEP_UM,
        dtype=float,
    )

    validate_mark1300_reduction()

    mark1300_results: dict[str, dict[str, object]] = {}
    for case_name, beam_fwhm_um in MARK1300_BEAM_CASES.items():
        fraction_by_sigma = {
            sigma_nm: mark1300_left_fraction_scan(
                beam_fwhm_um,
                offsets_um,
                sigma_nm,
                sigma_nm,
                q_mask_shift_nm_inv=q_mask_shift_nm_inv,
            )
            for sigma_nm in sigmas_nm
        }
        mark1300_results[case_name] = {
            "beam_fwhm_um": beam_fwhm_um,
            "offsets_um": offsets_um,
            "fraction_by_sigma": fraction_by_sigma,
        }
        table_path = output_dir / f"mark1300_left_fraction_{case_name}.dat"
        save_scan_table(
            table_path,
            offsets_um,
            sigmas_nm,
            fraction_by_sigma,
            q_mask_shift_nm_inv,
        )
        print(f"Saved {table_path}")

    mark1300_summary_path = output_dir / "mark1300_selected_offsets.csv"
    save_selected_offset_summary(
        mark1300_summary_path,
        mark1300_results,
        sigmas_nm,
        q_mask_shift_nm_inv,
    )
    print(f"Saved {mark1300_summary_path}")

    mark1300_effect_path = output_dir / "mark1300_sigma_effect_summary.csv"
    save_sigma_effect_summary(
        mark1300_effect_path,
        mark1300_results,
        sigmas_nm,
        q_mask_shift_nm_inv,
    )
    print(f"Saved {mark1300_effect_path}")

    if not args.no_plot:
        erik = load_erik_motor_reference()
        mark1300_figure_path = output_dir / "mark1300_symmetric_sigma.png"
        figure_paths = save_comparison_plot(
            mark1300_figure_path,
            mark1300_results,
            sigmas_nm,
            title=(
                ""
            ),
            fraction_label=r"$f_L$",
            motor_offsets_um=erik["motor_offsets_um"],
            motor_left_fraction=erik["motor_left_fraction"],
        )
        for figure_path in figure_paths:
            print(f"Saved {figure_path}")

    print(
        "Completed symmetric-sigma sweep with q-mask shift "
        f"{q_mask_shift_nm_inv:+g} nm^-1."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
