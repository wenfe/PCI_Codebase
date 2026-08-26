"""Generate compact report assets from already-computed SAXS/PCI results.

This script does not rerun the 4096^2 wave-propagation notebooks.  It reads
their saved tables and figures, makes one cross-workflow summary plot, and
builds a GIF from the nine saved PCI-exit/SAXS-detector comparison frames.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
from PIL import Image


HERE = Path(__file__).resolve().parent
OUTPUTS = HERE / "outputs"
ASSET_DIR = HERE.parent / "docs" / "saxs_pci_results_assets"
ASSET_DIR.mkdir(parents=True, exist_ok=True)


def left_fraction(table: np.ndarray) -> np.ndarray:
    return table[:, 1] / (table[:, 1] + table[:, 2])


def load_first_table(*paths: Path) -> np.ndarray:
    """Load the first available saved-table variant."""
    for path in paths:
        if path.exists():
            return np.loadtxt(path)
    candidates = ", ".join(str(path) for path in paths)
    raise FileNotFoundError(f"None of the expected result tables exists: {candidates}")


def load_divergence_table(path: Path) -> dict[str, np.ndarray]:
    rows = np.genfromtxt(path, delimiter="\t", names=True, dtype=None, encoding="utf-8")
    result: dict[str, np.ndarray] = {}
    for case in np.unique(rows["case"]):
        # Older method tables append a provenance suffix to the 6 um case.
        # Keep the plotting key stable across both table variants.
        key = str(case).removesuffix(" (method 1)")
        result[key] = rows[rows["case"] == case]
    return result


def make_summary_plot() -> Path:
    saxs_75 = np.loadtxt(
        OUTPUTS / "saxs" / "tables" / "DivSAXS_asymmetry_Mark1300_7p5um.dat"
    )
    saxs_60 = load_first_table(
        OUTPUTS / "saxs" / "tables" / "DivSAXS_asymmetry_Mark1300_6um.dat",
        OUTPUTS / "saxs" / "tables" / "DivSAXS_asymmetry_Mark1300_6um_lg.dat",
    )
    pci = np.loadtxt(OUTPUTS / "clean_pci" / "pci_exit_left_right_vs_offset.dat")

    erik_dir = HERE / "inputs" / "experimental" / "Erik"
    erik_x = np.load(erik_dir / "pos_grid.npy").astype(float) / 1e3
    erik_ratio = np.load(erik_dir / "left_div_right.npy").astype(float)
    erik_fraction = erik_ratio / (1.0 + erik_ratio)
    exp_x = np.load(erik_dir / "motor_positions_um.npy").astype(float)
    exp_fraction = np.load(erik_dir / "left_div_left_right_exp.npy").astype(float)

    transmission = np.loadtxt(HERE / "inputs" / "experimental" / "MotoPosition_Zyla_r0484.dat")
    if transmission.shape[0] != 3:
        transmission = transmission.T
    transmission_x = (transmission[0] - transmission[0, np.nanargmin(transmission[2])]) * 1e3
    transmission_y = transmission[2] / np.nanmax(transmission[2])

    divergence_cases = load_divergence_table(
        OUTPUTS / "methods" / "tables" / "DivSAXS_divergence_vs_offset_Methods.dat"
    )

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)

    ax = axes[0, 0]
    ax.plot(saxs_75[:, 0] / 1e3, left_fraction(saxs_75), "o-", ms=3,
            label="Wen SAXS, 7.5 µm")
    ax.plot(saxs_60[:, 0] / 1e3, left_fraction(saxs_60), "s-", ms=3,
            label="Lingen SAXS, 6.0 µm")
    ax.plot(erik_x, erik_fraction, "-", lw=2, label="Erik collimated simulation")
    ax.plot(exp_x, exp_fraction, "kx", ms=5, label="Experiment")
    ax.axhline(0.5, color="0.25", lw=1)
    ax.set(xlabel="Wire offset [µm]", ylabel="SAXS left fraction  L/(L+R)",
           title="A. SAXS Left Fraction", ylim=(0.15, 0.85))
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.plot(pci[:, 0], pci[:, 1], label="PCI exit: left / incident total")
    ax.plot(pci[:, 0], pci[:, 2], label="PCI exit: right / incident total")
    ax.plot(pci[:, 0], pci[:, 3], lw=2.5, label="PCI exit: total / incident total")
    ax.plot(transmission_x, transmission_y, "ko", ms=3.5,
            label="Experiment r0484 (own-max normalized)")
    ax.set(xlabel="Wire offset [µm]", ylabel="Transmitted intensity/incident intensity",
           title="B. Target-exit transmission", xlim=(-10.5, 10.5))
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    case_order = [
        "collimated",
        "6 um FWHM",
        "9 um FWHM",
        "12 um FWHM",
    ]
    labels = {
        "collimated": "12 µm, large-waist branch",
        "6 um FWHM": "6 µm, divergent branch",
        "9 um FWHM": "9 µm, divergent branch",
        "12 um FWHM": "12 µm, divergent branch",
    }
    for case in case_order:
        rows = divergence_cases[case]
        divergence = float(rows["divergence_urad"][0])
        ax.plot(
            rows["offset_um"],
            rows["left_fraction"],
            "o-",
            ms=4,
            label=f"{labels[case]}, div {divergence:.1f} µrad",
        )
    ax.axhline(0.5, color="0.25", lw=1)
    ax.set(
        xlabel="Wire offset [µm]",
        ylabel="SAXS left fraction  L/(L+R)",
        title="C. Offset calibration vs source divergence",
        ylim=(0.18, 0.82),
    )
    ax.legend(fontsize=8)

    # Panel D uses the saved scans to summarize the three quantities varied in
    # the simulations.  The top plots report global SAXS calibration slopes;
    # the lower plot shows the two direct offset responses.
    ax = axes[1, 1]
    ax.set_title("D. Statistics of the three varied simulation factors")
    ax.axis("off")

    profile_fwhm = np.array([6.0, 7.5])
    profile_slopes = np.array([
        np.polyfit(saxs_60[:, 0] / 1e3, left_fraction(saxs_60), 1)[0],
        np.polyfit(saxs_75[:, 0] / 1e3, left_fraction(saxs_75), 1)[0],
    ])

    divergence_values = np.array([
        float(divergence_cases[case]["divergence_urad"][0]) for case in case_order
    ])
    divergence_slopes = np.array([
        np.polyfit(
            divergence_cases[case]["offset_um"],
            divergence_cases[case]["left_fraction"],
            1,
        )[0]
        for case in case_order
    ])
    divergence_order = np.argsort(divergence_values)
    divergence_r = np.corrcoef(divergence_values, divergence_slopes)[0, 1]

    saxs_offset = saxs_75[:, 0] / 1e3
    saxs_fraction = left_fraction(saxs_75)
    saxs_r = np.corrcoef(saxs_offset, saxs_fraction)[0, 1]
    pci_abs_offset_r = np.corrcoef(np.abs(pci[:, 0]), pci[:, 3])[0, 1]

    profile_ax = ax.inset_axes([0.08, 0.59, 0.39, 0.33])
    profile_ax.plot(profile_fwhm, profile_slopes, "o-", color="#276FBF", lw=1.5, ms=5)
    profile_ax.axhline(profile_slopes.mean(), color="0.45", ls="--", lw=0.8)
    for x_value, y_value in zip(profile_fwhm, profile_slopes):
        profile_ax.annotate(
            f"{y_value:.4f}",
            (x_value, y_value),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7,
        )
    profile_pad = max(np.ptp(profile_slopes) * 0.55, 0.00035)
    profile_ax.set_ylim(profile_slopes.min() - profile_pad, profile_slopes.max() + profile_pad)
    profile_ax.set_xticks(profile_fwhm)
    profile_ax.set(
        title=(
            "Beam profile: global slope\n"
            rf"mean $\pm$ SD = {profile_slopes.mean():.4f} $\pm$ "
            rf"{profile_slopes.std(ddof=1):.4f} $\mu$m$^{{-1}}$"
        ),
        xlabel=r"Beam FWHM [$\mu$m]",
        ylabel=r"$df_L/dx$ [$\mu$m$^{-1}$]",
    )

    divergence_ax = ax.inset_axes([0.58, 0.59, 0.39, 0.33])
    divergence_ax.plot(
        divergence_values[divergence_order],
        divergence_slopes[divergence_order],
        "o-",
        color="#7A4EAB",
        lw=1.5,
        ms=5,
    )
    divergence_ax.axhline(divergence_slopes.mean(), color="0.45", ls="--", lw=0.8)
    divergence_ax.set(
        title=(
            "Divergence: global slope\n"
            f"Pearson $r$ = {divergence_r:.2f}; mean = {divergence_slopes.mean():.4f}"
        ),
        xlabel=r"Divergence [$\mu$rad]",
        ylabel=r"$df_L/dx$ [$\mu$m$^{-1}$]",
    )

    offset_ax = ax.inset_axes([0.08, 0.10, 0.89, 0.36])
    offset_ax.plot(
        saxs_offset,
        saxs_fraction,
        "o-",
        color="#2E7D32",
        lw=1.6,
        ms=2.8,
        label=(
            f"SAXS $f_L$: $r(x,f_L)$={saxs_r:.3f}, "
            f"range={np.ptp(saxs_fraction):.3f}"
        ),
    )
    offset_ax.plot(
        pci[:, 0],
        pci[:, 3],
        "s-",
        color="#B23A48",
        lw=1.6,
        ms=2.8,
        label=(
            f"PCI transmission: $r(|x|,T)$={pci_abs_offset_r:.3f}, "
            f"range={np.ptp(pci[:, 3]):.3f}"
        ),
    )
    offset_ax.axhline(0.5, color="0.45", lw=0.8)
    offset_ax.set(
        title="Wire-offset response",
        xlabel=r"Wire offset [$\mu$m]",
        ylabel="Normalized response",
        xlim=(-10.5, 10.5),
        ylim=(0.18, 1.02),
    )
    offset_ax.legend(fontsize=6.7, loc="center right")

    for inset_ax in (profile_ax, divergence_ax, offset_ax):
        inset_ax.tick_params(labelsize=7)
        inset_ax.title.set_fontsize(8)
        inset_ax.xaxis.label.set_fontsize(7.5)
        inset_ax.yaxis.label.set_fontsize(7.5)

    fig.suptitle("SAXS–PCI results: offset, transmission, divergence, and influence factors", fontsize=15)
    path = ASSET_DIR / "summary_key_results.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def make_offset_gif() -> Path:
    figure_dir = OUTPUTS / "experimental_comparison" / "figures"
    tags = ["m10p0", "m7p5", "m5p0", "m2p5", "p0p0", "p2p5", "p5p0", "p7p5", "p10p0"]
    files = [figure_dir / f"01_exit_pci_and_saxs_offset_{tag}um.png" for tag in tags]
    frames: list[Image.Image] = []
    for path in files:
        with Image.open(path) as image:
            frame = image.convert("RGB")
            if frame.width > 1000:
                height = round(frame.height * 1000 / frame.width)
                frame = frame.resize((1000, height), Image.Resampling.LANCZOS)
            frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=192))

    output = ASSET_DIR / "saxs_pci_experimental_offset_scan.gif"
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=650,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return output


if __name__ == "__main__":
    make_summary_plot()
    make_offset_gif()

