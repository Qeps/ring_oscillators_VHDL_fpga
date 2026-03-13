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


def load_series_from_file(path: Path) -> list[np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    series: list[np.ndarray] = []
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
                    "Inconsistent series length in input file: "
                    f"line {line_no} has {len(bits)} bits, expected {expected_length}."
                )

            series.append(bits)

    if not series:
        raise ValueError("No bit series found in input file.")

    return series


def build_plot_path(series_idx: int, suffix: str) -> Path | None:
    if not SAVE_PLOTS:
        return None
    return OUT_PREFIX.parent / f"{OUT_PREFIX.name}_s{series_idx:03d}_{suffix}"


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
) -> None:
    max_val = 2**word_size
    if bins is None:
        bins = min(max_val, 256)

    plt.figure(figsize=(7, 7))
    plt.hist2d(x, y, bins=bins)
    plt.xlabel("w[n]")
    plt.ylabel(f"w[n+{tau}]")
    plt.title(
        f"2D delay map, word_size={word_size}, tau={tau}\n"
        f"bits={bit_count}, words={word_count}, pairs={len(x)}"
    )
    plt.colorbar(label="Count")

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()


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


def analyze_series(bits: np.ndarray, series_idx: int, series_count: int) -> None:
    print(f"\nSeries {series_idx}/{series_count}: {len(bits)} bits")

    total_maps = len(MAP2D_WORD_SIZES) * len(MAP2D_TAUS)
    map_idx = 0

    for word_size in MAP2D_WORD_SIZES:
        step = STEP if STEP is not None else word_size
        words = bits_to_words(bits, word_size, step=step)
        print(f"Built {len(words)} words of {word_size} bits (step={step}).")

        for tau in MAP2D_TAUS:
            map_idx += 1
            x, y = delay_pairs(words, tau)
            print(f"Generating map {map_idx}/{total_maps}: word_size={word_size}, tau={tau}")
            plot_delay_map_2d(
                x,
                y,
                bit_count=len(bits),
                word_count=len(words),
                word_size=word_size,
                tau=tau,
                bins=MAP2D_BINS,
                output=build_plot_path(series_idx, f"map2d_w{word_size}_tau{tau}.png"),
            )


def main() -> None:
    validate_config()

    print(f"Loading captured series from: {ANALYSIS_INPUT_PATH}")
    series = load_series_from_file(ANALYSIS_INPUT_PATH)
    print(f"Loaded {len(series)} series, {len(series[0])} bits each.")

    for idx, bits in enumerate(series, start=1):
        analyze_series(bits, idx, len(series))


if __name__ == "__main__":
    main()
