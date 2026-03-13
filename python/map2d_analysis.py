from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from user_param import ANALYSIS_INPUT_PATH, MAP2D_BINS, MAP2D_TAUS, MAP2D_WORD_SIZES, OUT_PREFIX, SAVE_PLOTS, STEP


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


def build_plot_path(bitstream_idx: int, suffix: str) -> Path | None:
    if not SAVE_PLOTS:
        return None
    return OUT_PREFIX.parent / f"{OUT_PREFIX.name}_b{bitstream_idx:03d}_{suffix}"


def bits_to_words(bits: np.ndarray, word_size: int, step: int = 1) -> np.ndarray:
    if word_size < 1 or word_size > 32:
        raise ValueError("WORD_SIZE must be in range 1..32.")
    if step < 1:
        raise ValueError("STEP must be >= 1.")

    n = len(bits)
    if n < word_size:
        raise ValueError("Not enough bits to build words.")

    words = []
    for i in range(0, n - word_size + 1, step):
        word = 0
        for j in range(word_size):
            word = (word << 1) | int(bits[i + j])
        words.append(word)

    return np.array(words, dtype=np.uint32)


def delay_pairs(words: np.ndarray, tau: int) -> tuple[np.ndarray, np.ndarray]:
    if tau < 0:
        raise ValueError("TAU must be >= 0.")
    if len(words) <= tau:
        raise ValueError("Not enough words for 2D delay map.")
    if tau == 0:
        return words, words

    return words[:-tau], words[tau:]


def plot_delay_map_2d(
    x: np.ndarray,
    y: np.ndarray,
    bit_count: int,
    word_count: int,
    word_size: int,
    tau: int,
    bins: int | None = None,
    output: Path | None = None,
) -> dict[str, int | float]:
    max_val = 2**word_size
    if bins is None:
        bins = min(max_val, 256)

    hist, xedges, yedges = np.histogram2d(
        x,
        y,
        bins=bins,
        range=[[0, max_val], [0, max_val]],
    )
    occupied_bins = int(np.count_nonzero(hist))
    total_bins = int(hist.size)
    max_bin_count = int(hist.max()) if total_bins > 0 else 0
    fill_ratio = occupied_bins / total_bins if total_bins > 0 else 0.0
    diagonal_share = float(np.trace(hist)) / len(x) if len(x) > 0 else 0.0

    fig, ax = plt.subplots(figsize=(7, 7))
    mesh = ax.pcolormesh(xedges, yedges, hist.T, shading="auto")
    ax.set_xlabel("w[n]")
    ax.set_ylabel(f"w[n+{tau}]")
    ax.set_title(
        f"2D delay map, word_size={word_size}, tau={tau}\n"
        f"bits={bit_count}, words={word_count}, pairs={len(x)}"
    )
    fig.colorbar(mesh, ax=ax, label="Count")

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)

    return {
        "word_size": word_size,
        "tau": tau,
        "word_count": word_count,
        "pair_count": len(x),
        "bins": int(bins),
        "occupied_bins": occupied_bins,
        "fill_ratio": fill_ratio,
        "diagonal_share": diagonal_share,
        "max_bin_count": max_bin_count,
    }


def render_map2d_table(
    results: list[dict[str, int | float]],
    bit_count: int,
    bitstream_idx: int,
    bitstream_count: int,
    output: Path | None = None,
) -> None:
    if not results:
        return

    headers = [
        "Word",
        "Tau",
        "Words",
        "Pairs",
        "Grid",
        "Occupied",
        "Fill %",
        "Diag %",
        "Max bin",
    ]
    rows: list[list[str]] = []
    row_colors: list[list[str]] = []

    for idx, result in enumerate(results):
        bins = int(result["bins"])
        rows.append(
            [
                str(int(result["word_size"])),
                str(int(result["tau"])),
                str(int(result["word_count"])),
                str(int(result["pair_count"])),
                f"{bins}x{bins}",
                str(int(result["occupied_bins"])),
                f"{100.0 * float(result['fill_ratio']):.2f}",
                f"{100.0 * float(result['diagonal_share']):.2f}",
                str(int(result["max_bin_count"])),
            ]
        )
        base_color = "#ffffff" if idx % 2 == 0 else "#f7f7f7"
        row_colors.append([base_color] * len(headers))

    figure_height = max(5.0, 1.8 + 0.34 * len(rows))
    fig, ax = plt.subplots(figsize=(11.5, figure_height))
    ax.axis("off")

    fig.suptitle(
        f"2D map summary: bitstream {bitstream_idx}/{bitstream_count}, bits={bit_count}",
        fontsize=15,
        y=0.98,
    )

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        colLoc="center",
        cellColours=row_colors,
        bbox=[0.02, 0.08, 0.96, 0.84],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.3)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#d9e2f3")
            cell.set_text_props(weight="bold")

    fig.text(
        0.02,
        0.02,
        "Diag % = share of pairs on histogram diagonal, Fill % = occupied cells / all cells.",
        fontsize=9,
    )

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def validate_config() -> None:
    if not MAP2D_WORD_SIZES:
        raise ValueError("MAP2D_WORD_SIZES must not be empty.")
    if not MAP2D_TAUS:
        raise ValueError("MAP2D_TAUS must not be empty.")
    for word_size in MAP2D_WORD_SIZES:
        if word_size < 1 or word_size > 32:
            raise ValueError("Each MAP2D_WORD_SIZES value must be in range 1..32.")
    for tau in MAP2D_TAUS:
        if tau < 0:
            raise ValueError("Each MAP2D_TAUS value must be >= 0.")
    if STEP is not None and STEP < 1:
        raise ValueError("STEP must be >= 1.")


def analyze_bitstream(bits: np.ndarray, bitstream_idx: int, bitstream_count: int) -> None:
    print(f"\nBitstream {bitstream_idx}/{bitstream_count}: {len(bits)} bits")

    total_maps = len(MAP2D_WORD_SIZES) * len(MAP2D_TAUS)
    map_idx = 0
    map_results: list[dict[str, int | float]] = []

    for word_size in MAP2D_WORD_SIZES:
        step = STEP if STEP is not None else word_size
        words = bits_to_words(bits, word_size, step=step)
        print(f"Built {len(words)} words of {word_size} bits (step={step}).")

        for tau in MAP2D_TAUS:
            map_idx += 1
            x, y = delay_pairs(words, tau)
            print(f"Generating map {map_idx}/{total_maps}: word_size={word_size}, tau={tau}")
            map_results.append(
                plot_delay_map_2d(
                x,
                y,
                bit_count=len(bits),
                word_count=len(words),
                word_size=word_size,
                tau=tau,
                bins=MAP2D_BINS,
                output=build_plot_path(bitstream_idx, f"map2d_w{word_size}_tau{tau}.png"),
                )
            )

    render_map2d_table(
        map_results,
        bit_count=len(bits),
        bitstream_idx=bitstream_idx,
        bitstream_count=bitstream_count,
        output=build_plot_path(bitstream_idx, "map2d_summary.png"),
    )


def main() -> None:
    validate_config()

    print(f"Loading captured bitstreams from: {ANALYSIS_INPUT_PATH}")
    bitstreams = load_bitstreams_from_file(ANALYSIS_INPUT_PATH)
    print(f"Loaded {len(bitstreams)} bitstreams, {len(bitstreams[0])} bits each.")

    for idx, bits in enumerate(bitstreams, start=1):
        analyze_bitstream(bits, idx, len(bitstreams))


if __name__ == "__main__":
    main()
