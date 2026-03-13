from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from user_param import ANALYSIS_INPUT_PATH, MAX_LAG, OUT_PREFIX, SAVE_PLOTS


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


def validate_config() -> None:
    if MAX_LAG < 0:
        raise ValueError("MAX_LAG must be >= 0.")


def analyze_series(bits: np.ndarray, series_idx: int, series_count: int) -> None:
    print(f"\nSeries {series_idx}/{series_count}: {len(bits)} bits")

    max_lag_for_series = min(MAX_LAG, len(bits) - 1)
    if max_lag_for_series < 0:
        print("Autocorrelation skipped: not enough bits.")
        return

    ac = autocorrelation(bits, max_lag_for_series)
    lag_min = 0
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


def main() -> None:
    validate_config()

    print(f"Loading captured series from: {ANALYSIS_INPUT_PATH}")
    series = load_series_from_file(ANALYSIS_INPUT_PATH)
    print(f"Loaded {len(series)} series, {len(series[0])} bits each.")

    for idx, bits in enumerate(series, start=1):
        analyze_series(bits, idx, len(series))


if __name__ == "__main__":
    main()
