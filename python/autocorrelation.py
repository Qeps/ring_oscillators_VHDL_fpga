from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from user_func import bitstream_length_summary, build_output_path, load_bitstreams_from_file
from user_param import ANALYSIS_INPUT_PATH, MAX_LAG


def autocorrelation(bits: np.ndarray, max_lag: int) -> np.ndarray:
    if len(bits) < max_lag + 1:
        raise ValueError("Not enough bits for MAX_LAG.")

    x = bits.astype(np.int8) * 2 - 1
    ac = np.empty(max_lag + 1, dtype=np.float64)

    for lag in range(max_lag + 1):
        a = x[: len(x) - lag]
        b = x[lag:]
        ac[lag] = np.mean(a * b)

    return ac


def plot_autocorrelation(
    ac: np.ndarray,
    lag_min: int,
    lag_max: int,
    output: Path | None = None,
) -> None:
    if lag_min < 0:
        raise ValueError("lag_min must be >= 0.")
    if lag_max < lag_min:
        raise ValueError("lag_max must be >= lag_min.")
    if lag_max >= len(ac):
        raise ValueError("lag_max is out of range for autocorrelation array.")

    lags = np.arange(lag_min, lag_max + 1)
    values = ac[lag_min : lag_max + 1]

    fig, (ax_full, ax_zoom) = plt.subplots(
        2,
        1,
        figsize=(10, 7),
        sharex=True,
        height_ratios=(2, 3),
        constrained_layout=True,
    )

    ax_full.stem(lags, values, basefmt=" ")
    ax_full.set_ylabel("Autocorrelation")
    ax_full.set_title(f"Bitstream autocorrelation (lags {lag_min}-{lag_max})")
    ax_full.grid(True)

    zoom_lags = lags[1:] if lag_min == 0 and len(lags) > 1 else lags
    zoom_values = values[1:] if lag_min == 0 and len(values) > 1 else values

    ax_zoom.stem(zoom_lags, zoom_values, basefmt=" ")
    ax_zoom.axhline(0.0, color="black", linewidth=1.0)
    ax_zoom.set_xlabel("Lag")
    ax_zoom.set_ylabel("Zoom")
    ax_zoom.grid(True)

    if len(zoom_values) > 0:
        max_abs = np.max(np.abs(zoom_values))
        ax_zoom.set_ylim(-1.2 * max_abs, 1.2 * max_abs)
    else:
        ax_zoom.text(0.5, 0.5, "No lags > 0 in selected range.", ha="center", va="center", transform=ax_zoom.transAxes)
        ax_zoom.set_ylim(-1.0, 1.0)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def render_autocorrelation_table(
    ac: np.ndarray,
    bit_count: int,
    bitstream_idx: int,
    bitstream_count: int,
    lag_min: int,
    lag_max: int,
    output: Path | None = None,
) -> None:
    if lag_min < 0:
        raise ValueError("lag_min must be >= 0.")
    if lag_max < lag_min:
        raise ValueError("lag_max must be >= lag_min.")
    if lag_max >= len(ac):
        raise ValueError("lag_max is out of range for autocorrelation array.")

    headers = ["Lag", "R"]
    rows: list[list[str]] = []
    row_colors: list[list[str]] = []

    for lag in range(lag_min, lag_max + 1):
        rows.append([str(lag), f"{float(ac[lag]):+.6f}"])
        base_color = "#d9e2f3" if lag == 0 else ("#ffffff" if lag % 2 == 0 else "#f7f7f7")
        row_colors.append([base_color, base_color])

    figure_height = max(4.0, 1.8 + 0.32 * len(rows))
    fig, ax = plt.subplots(figsize=(6.0, figure_height))
    ax.axis("off")

    fig.suptitle(
        f"Autocorrelation summary: bitstream {bitstream_idx}/{bitstream_count}, bits={bit_count}",
        fontsize=15,
        y=0.98,
    )

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        colLoc="center",
        cellColours=row_colors,
        bbox=[0.12, 0.08, 0.76, 0.84],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.35)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#d9e2f3")
            cell.set_text_props(weight="bold")
        elif row == 1:
            cell.set_text_props(weight="bold")

    fig.text(0.12, 0.02, f"Lags shown: {lag_min}..{lag_max}", fontsize=9)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def validate_config() -> None:
    if MAX_LAG < 0:
        raise ValueError("MAX_LAG must be >= 0.")


def analyze_bitstream(bits: np.ndarray, bitstream_idx: int, bitstream_count: int) -> None:
    print(f"\nBitstream {bitstream_idx}/{bitstream_count}: {len(bits)} bits")

    max_lag_for_bitstream = min(MAX_LAG, len(bits) - 1)
    if max_lag_for_bitstream < 0:
        print("Autocorrelation skipped: not enough bits.")
        return

    ac = autocorrelation(bits, max_lag_for_bitstream)
    lag_min = 0
    lag_max = min(max_lag_for_bitstream, 15)
    print(f"Autocorrelation (lags {lag_min}..{lag_max}):")
    for lag, value in enumerate(ac[lag_min : lag_max + 1], start=lag_min):
        print(f"lag={lag:2d}, R={value:+.6f}")

    plot_autocorrelation(
        ac,
        lag_min=lag_min,
        lag_max=lag_max,
        output=build_output_path("autocorr.png", bitstream_idx),
    )
    render_autocorrelation_table(
        ac,
        bit_count=len(bits),
        bitstream_idx=bitstream_idx,
        bitstream_count=bitstream_count,
        lag_min=lag_min,
        lag_max=lag_max,
        output=build_output_path("autocorr_table.png", bitstream_idx),
    )


def main() -> None:
    validate_config()

    print(f"Loading captured bitstreams from: {ANALYSIS_INPUT_PATH}")
    bitstreams = load_bitstreams_from_file(ANALYSIS_INPUT_PATH)
    print(f"Loaded {bitstream_length_summary(bitstreams)}")

    for idx, bits in enumerate(bitstreams, start=1):
        analyze_bitstream(bits, idx, len(bitstreams))


if __name__ == "__main__":
    main()
