from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from user_param import (
    ANALYSIS_INPUT_PATH,
    MAP2D_BINS,
    MAX_LAG,
    MODE,
    OUT_PREFIX,
    SAVE_PLOTS,
    STEP,
    TAU,
    WORD_SIZE,
)


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


def autocorrelation(bits: np.ndarray, max_lag: int) -> np.ndarray:
    if len(bits) < max_lag + 2:
        raise ValueError("Not enough bits for MAX_LAG.")

    x = bits.astype(np.int8) * 2 - 1
    ac = np.empty(max_lag + 1, dtype=np.float64)

    for lag in range(max_lag + 1):
        a = x[: len(x) - lag]
        b = x[lag:]
        ac[lag] = np.mean(a * b)

    return ac


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
    if tau < 1:
        raise ValueError("TAU must be >= 1.")
    if len(words) <= tau:
        raise ValueError("Not enough words for 2D delay map.")

    return words[:-tau], words[tau:]


def plot_autocorrelation(
    ac: np.ndarray,
    lag_min: int,
    lag_max: int,
    output: Path | None = None,
) -> None:
    if lag_min < 1:
        raise ValueError("lag_min must be >= 1.")
    if lag_max < lag_min:
        raise ValueError("lag_max must be >= lag_min.")
    if lag_max >= len(ac):
        raise ValueError("lag_max is out of range for autocorrelation array.")

    lags = np.arange(lag_min, lag_max + 1)
    values = ac[lag_min : lag_max + 1]

    plt.figure(figsize=(10, 4))
    plt.stem(lags, values)
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.title(f"Bitstream autocorrelation (lags {lag_min}-{lag_max})")
    plt.grid(True)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()


def plot_delay_map_2d(
    x: np.ndarray,
    y: np.ndarray,
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
    plt.title(f"2D delay map, word_size={word_size}, tau={tau}")
    plt.colorbar(label="Count")

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=200, bbox_inches="tight")
    else:
        plt.show()


def build_plot_path(series_idx: int, suffix: str) -> Path | None:
    if not SAVE_PLOTS:
        return None
    return OUT_PREFIX.parent / f"{OUT_PREFIX.name}_s{series_idx:03d}_{suffix}"


def validate_config() -> None:
    if MAX_LAG < 1:
        raise ValueError("MAX_LAG must be >= 1.")
    if WORD_SIZE < 1 or WORD_SIZE > 32:
        raise ValueError("WORD_SIZE must be in range 1..32.")
    if TAU < 1:
        raise ValueError("TAU must be >= 1.")
    if MODE not in {"ac", "map2d", "all"}:
        raise ValueError("MODE must be one of: ac, map2d, all.")


def analyze_series(bits: np.ndarray, series_idx: int, series_count: int) -> None:
    print(f"\nSeries {series_idx}/{series_count}: {len(bits)} bits")

    if MODE in ("ac", "all"):
        max_lag_for_series = min(MAX_LAG, len(bits) - 2)
        if max_lag_for_series >= 1:
            ac = autocorrelation(bits, max_lag_for_series)
            lag_min = 1
            lag_max = min(max_lag_for_series, 15)
            print(f"Autocorrelation (lags {lag_min}..{lag_max}):")
            for lag, value in enumerate(ac[lag_min : lag_max + 1], start=lag_min):
                print(f"lag={lag:2d}, R={value:+.6f}")
            plot_autocorrelation(
                ac,
                lag_min=lag_min,
                lag_max=lag_max,
                output=build_plot_path(series_idx, "autocorr.png"),
            )
        else:
            print("Autocorrelation skipped: not enough bits.")

    if MODE in ("map2d", "all"):
        words = bits_to_words(bits, WORD_SIZE, step=STEP)
        print(f"Built {len(words)} words of {WORD_SIZE} bits (step={STEP}).")
        x, y = delay_pairs(words, TAU)
        plot_delay_map_2d(
            x,
            y,
            WORD_SIZE,
            TAU,
            bins=MAP2D_BINS,
            output=build_plot_path(series_idx, f"map2d_tau{TAU}.png"),
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
