from pathlib import Path
from math import erfc, sqrt

import matplotlib.pyplot as plt
import numpy as np

from user_param import ANALYSIS_INPUT_PATH, BIAS_ALPHA, OUT_PREFIX, SAVE_PLOTS


def parse_bits_line(bit_text: str, line_no: int) -> np.ndarray:
    raw = bit_text.encode("ascii")
    data = np.frombuffer(raw, dtype=np.uint8)

    valid = (data == ord("0")) | (data == ord("1"))
    if not np.all(valid):
        raise ValueError(f"Invalid character in input file at line {line_no}. Allowed: '0'/'1'.")

    return (data - ord("0")).astype(np.uint8, copy=False)


def load_bitstreams_from_file(path: Path) -> list[np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    bitstreams: list[np.ndarray] = []
    expected_length: int | None = None

    with path.open("r", encoding="ascii") as f:
        for line_no, line in enumerate(f, start=1):
            bit_text = line.strip()
            if not bit_text or bit_text.startswith("#"):
                continue

            bits = parse_bits_line(bit_text, line_no)
            if expected_length is None:
                expected_length = len(bits)
            elif len(bits) != expected_length:
                raise ValueError(
                    "Inconsistent bitstream length in input file: "
                    f"line {line_no} has {len(bits)} bits, expected {expected_length}."
                )

            bitstreams.append(bits)

    if not bitstreams:
        raise ValueError("No bitstreams found in input file.")

    return bitstreams


def build_plot_path(suffix: str) -> Path | None:
    if not SAVE_PLOTS:
        return None
    return OUT_PREFIX.parent / f"{OUT_PREFIX.name}_{suffix}"


def analyze_bitstream(bits: np.ndarray, bitstream_idx: int, bitstream_count: int) -> dict[str, float | int | bool]:
    total_bits = len(bits)
    one_count = int(np.count_nonzero(bits))
    zero_count = total_bits - one_count
    p_one = one_count / total_bits
    p_zero = zero_count / total_bits
    bias_01 = p_one - 0.5
    mean_pm1 = 2.0 * p_one - 1.0
    sigma_bias = 0.5 / sqrt(total_bits)
    s_n = one_count - zero_count
    s_obs = abs(s_n) / sqrt(total_bits)
    p_value = erfc(s_obs / sqrt(2.0))
    passed = p_value >= BIAS_ALPHA

    print(f"\nBitstream {bitstream_idx}/{bitstream_count}: {total_bits} bits")
    print(f"zeros={zero_count}, ones={one_count}")
    print(f"P(0)={p_zero:.6f}, P(1)={p_one:.6f}")
    print(f"Bias P(1)-0.5 = {bias_01:+.6f}")
    print(f"Mean of mapped +/-1 sequence = {mean_pm1:+.6f}")
    print(f"Reference bands for P(1)-0.5: +/-2sigma={2.0 * sigma_bias:.6f}, +/-3sigma={3.0 * sigma_bias:.6f}")
    print(f"Monobit test: p_value={p_value:.6f}, alpha={BIAS_ALPHA:.4f}, result={'PASS' if passed else 'FAIL'}")

    return {
        "bitstream_idx": bitstream_idx,
        "total_bits": total_bits,
        "zero_count": zero_count,
        "one_count": one_count,
        "p_zero": p_zero,
        "p_one": p_one,
        "bias_01": bias_01,
        "mean_pm1": mean_pm1,
        "sigma_bias": sigma_bias,
        "p_value": p_value,
        "passed": passed,
    }


def render_bias_table(
    results: list[dict[str, float | int | bool]],
    overall_pass: bool,
    passed_count: int,
    output: Path | None = None,
) -> None:
    if not results:
        return

    headers = [
        "Bitstream",
        "Bits",
        "Zeros",
        "Ones",
        "P(0)",
        "P(1)",
        "Bias",
        "Mean +/-1",
        "p-value",
        "Result",
    ]
    rows: list[list[str]] = []
    row_colors: list[list[str]] = []

    for result in results:
        passed = bool(result["passed"])
        base_color = "#e8f5e9" if passed else "#ffebee"
        rows.append(
            [
                str(int(result["bitstream_idx"])),
                str(int(result["total_bits"])),
                str(int(result["zero_count"])),
                str(int(result["one_count"])),
                f"{float(result['p_zero']):.6f}",
                f"{float(result['p_one']):.6f}",
                f"{float(result['bias_01']):+.6f}",
                f"{float(result['mean_pm1']):+.6f}",
                f"{float(result['p_value']):.6f}",
                "PASS" if passed else "FAIL",
            ]
        )
        row_colors.append([base_color] * len(headers))

    figure_height = max(2.8, 1.6 + 0.45 * len(rows))
    fig, ax = plt.subplots(figsize=(14, figure_height))
    ax.axis("off")

    title = (
        f"Bias summary: {'PASS' if overall_pass else 'FAIL'} "
        f"({passed_count}/{len(results)} bitstreams passed, alpha={BIAS_ALPHA:.4f})"
    )
    fig.suptitle(title, fontsize=16, y=0.98)

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        colLoc="center",
        cellColours=row_colors,
        bbox=[0.02, 0.08, 0.96, 0.8],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.4)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#d9e2f3")
            cell.set_text_props(weight="bold")
        if col == len(headers) - 1 and row > 0:
            text = cell.get_text().get_text()
            cell.set_text_props(weight="bold", color="#1b5e20" if text == "PASS" else "#b71c1c")

    fig.text(
        0.02,
        0.02,
        "Columns: Bias = P(1)-0.5, Mean +/-1 = mean after mapping bits to {-1, +1}.",
        fontsize=9,
    )

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def main() -> None:
    print(f"Loading captured bitstreams from: {ANALYSIS_INPUT_PATH}")
    bitstreams = load_bitstreams_from_file(ANALYSIS_INPUT_PATH)
    print(f"Loaded {len(bitstreams)} bitstreams, {len(bitstreams[0])} bits each.")

    results: list[dict[str, float | int | bool]] = []
    for idx, bits in enumerate(bitstreams, start=1):
        results.append(analyze_bitstream(bits, idx, len(bitstreams)))

    passed_count = sum(bool(result["passed"]) for result in results)
    total_count = len(results)
    overall_pass = passed_count == total_count
    worst_result = min(results, key=lambda result: float(result["p_value"]))

    print("\nOverall bias result:")
    print(
        f"Monobit frequency test: {'PASS' if overall_pass else 'FAIL'} "
        f"({passed_count}/{total_count} bitstreams passed, alpha={BIAS_ALPHA:.4f})"
    )
    print(
        "Worst bitstream: "
        f"{int(worst_result['bitstream_idx'])}, "
        f"p_value={float(worst_result['p_value']):.6f}, "
        f"bias={float(worst_result['bias_01']):+.6f}"
    )

    render_bias_table(
        results,
        overall_pass=overall_pass,
        passed_count=passed_count,
        output=build_plot_path("bias_summary.png"),
    )


if __name__ == "__main__":
    main()
